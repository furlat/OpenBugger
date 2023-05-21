from libcst.codemod import CodemodContext, Codemod
from libcst import  Module
from typing import List

import libcst as cst
from libcst.codemod import CodemodContext, ContextAwareTransformer, ContextAwareVisitor
from libcst.metadata import BatchableMetadataProvider, PositionProvider, CodePosition, CodeRange
import libcst.matchers as m
import uuid

from openbugger.context import is_modified, save_modified, PositionContextUpdater


class Bugger(Codemod):
    """ A CodeMod that allows to chain multiple Transformers sharing the same context and reverse them"""  
    def __init__(self, transformers: List[ContextAwareTransformer]) -> None:
        
        self.context = CodemodContext()
        Codemod.__init__(self,self.context)
        self.transformers = [transformer(self.context) for transformer in transformers]
        self.inverse = InverseTransformer(self.context)
        self.position_updater = PositionContextUpdater(self.context)
        #the context scratchpad has an entry ["modfied_nodes"] indexed by the start position of the modified_nodes 
        self.debug = False
        self.debug_steps = []
    def print(self):
        print("original_code")
        if not self.original or not self.tainted:
            print("Run bugger.appply(module) before print")
        else:    
            print(self.original.code)
            print("tainted_code")
            print(self.tainted.code)
            bugged = self.original.deep_equals(self.tainted)
            print("The result of deep_equals between the concrete syntax tree of the original and the bugged code is {}".format(bugged))
            print("Checking for bugs...")
            self.print_bugs()
            if not self.clean:
                print("Run bugger.apply(bugger.tainted,debug=True) before print")
            else:    
                print("Debugging...")
                print("clean_code")
                print(self.clean.code)
                print("Checking if the debugged code is equal to the original code..")
                diff = self.original.deep_equals(self.clean)
                print("The result of deep_equals between the concrete syntax tree of the original and debugged code is {}".format(diff))
           
    def print_bugs(self):
        for modified in self.context.scratch.values():
            bug_type = modified["author"]
            pos = modified["original_position"]
            start_line, start_column = pos.start.line, pos.start.column
            end_line, end_column = pos.end.line, pos.end.column
            print("The following Node has a bug of type {} starting at line {}, column {} and ending at line {}, column {}.".format(bug_type,start_line,start_column,end_line,end_column))
            bugged_code = self.tainted.code_for_node(modified["updated_node"])
            debugged_code = self.original.code_for_node(modified["original_node"])
            print("The bug can be fixed by substituting the bugged code-string <{}> with the following code-string <{}>".format(bugged_code,debugged_code))

    def apply(self, tree:Module,debug:bool=False) ->Module:
        self.debug=debug
        return self.transform_module(tree)
    def transform_module_impl(self, tree: Module) -> Module:
        if not self.debug:
            self.original = tree
        tainted = tree
        for transformer in self.transformers:
            if self.debug:
                tainted=self.inverse.debug(tainted,transformer.id)
                self.debug_steps.append(tainted)
                
            else:
                tainted = transformer.mutate(tainted)
            tainted = self.position_updater.transform_module(tainted) 
        if self.debug: 
            self.clean=self.debug_steps[-1]
        else:       
            self.tainted = tainted   

        return tainted
    
class TestTransformer(ContextAwareTransformer):
        """ a test transformer that checks if a node has been modified by another transformer and if not pretends to modify it"""
        METADATA_DEPENDENCIES = (PositionProvider, )
        def __init__(
            self,
            context: CodemodContext):
            super().__init__(context)
            self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        def transform_module_impl(self, tree: cst.Module) -> cst.Module:
            return tree.visit(self)
        def mutate(self, tree: cst.Module,reverse: bool = False) -> cst.Module:
            return self.transform_module(tree)
        def taint_node(self, original_node:cst.CSTNode, updated_node: cst.CSTNode) ->   cst.CSTNode:
            meta_pos = self.get_metadata(PositionProvider, original_node)
            already_modified = is_modified(original_node,meta_pos,self.context)
            if not already_modified:
                # print("adding to scratch",meta_pos.start, meta_pos.end)
                updated_node = original_node
                save_modified(self.context,meta_pos,original_node,updated_node,self.id)
            return updated_node      
        def leave_ComparisonTarget(self, original_node:cst.ComparisonTarget, updated_node: cst.ComparisonTarget) -> None:
            return self.taint_node(original_node,updated_node)
        def leave_Assign(self, original_node:cst.Assign, updated_node: cst.Assign):
            return self.taint_node(original_node,updated_node)
        def leave_While(self, original_node:cst.While, updated_node: cst.While):
            return self.taint_node(original_node,updated_node)
        def leave_Comparison(self, original_node:cst.Comparison, updated_node: cst.Comparison):
            return self.taint_node(original_node,updated_node)
        def leave_Index(self, original_node:cst.Index, updated_node: cst.Index):
            return self.taint_node(original_node,updated_node)
        def leave_Slice(self, original_node:cst.Slice, updated_node: cst.Slice):
            return self.taint_node(original_node,updated_node)
        
def bugger_example(transformers,script):
    """ a method to automatically create an example of the bugger class applying the transformers to the script and visualizing the debugging process"""
    bugger = Bugger(transformers)
    # Parse the script into a CST
    module = cst.parse_module(script)
    tainted = bugger.apply(module)
    clean = bugger.apply(tainted,debug=True)
    bugger.print()

class InverseTransformer(ContextAwareTransformer):
        """ A transformer that inverts the changes made by other transformers that share the same context"""
        METADATA_DEPENDENCIES = (PositionProvider, )
        def __init__(
            self,
            context: CodemodContext):
            super().__init__(context)
            self.id = None
       
        def transform_module_impl(self, tree: cst.Module) -> cst.Module:
            return tree.visit(self)
        def debug(self, tree: cst.Module,id) -> cst.Module:
            self.id = id
            return self.transform_module(tree)
        def invert_node(self, original_node:cst.CSTNode, updated_node: cst.CSTNode) ->   cst.CSTNode:
            meta_pos = self.get_metadata(PositionProvider, original_node)
            #only updates nodes that are not already in the scratch
            already_modified  = [x for x in self.context.scratch.values() if meta_pos.start== x["original_position"].start]
            # if already_modified:
                # print("already found a node modified by",already_modified[0]["author"])
                # print("current author is",self.id)
            if already_modified and already_modified[0]["author"] == self.id:
                # print("reverting to old node",meta_pos.start, meta_pos.end)
                old_node= self.context.scratch[meta_pos.start]["original_node"]
                self.context.scratch[meta_pos.start]["debugged_node"]=old_node
                updated_node=old_node
            return updated_node   
        def leave_ComparisonTarget(self, original_node:cst.ComparisonTarget, updated_node: cst.ComparisonTarget) -> None:
            return self.invert_node(original_node,updated_node)
        def leave_Assign(self, original_node:cst.Assign, updated_node: cst.Assign):
            return self.invert_node(original_node,updated_node)
        def leave_While(self, original_node:cst.While, updated_node: cst.While):
            return self.invert_node(original_node,updated_node) 
        def leave_Comparison(self, original_node:cst.Comparison, updated_node: cst.Comparison):
            return self.invert_node(original_node,updated_node)        
        def leave_Index(self, original_node:cst.Index, updated_node: cst.Index):
            return self.invert_node(original_node,updated_node)
        def leave_Slice(self, original_node:cst.Slice, updated_node: cst.Slice):
            return self.invert_node(original_node,updated_node)
        def leave_ExceptHandler(self, original_node:cst.ExceptHandler, updated_node: cst.ExceptHandler):
            return self.invert_node(original_node,updated_node)
        def leave_Call(self, original_node:cst.Call, updated_node: cst.Call):
            return self.invert_node(original_node,updated_node)
        def leave_Return(self, original_node:cst.Return, updated_node: cst.Return):
            return self.invert_node(original_node,updated_node)
        def leave_List(self, original_node:cst.List, updated_node: cst.List):
            return self.invert_node(original_node,updated_node)
        def leave_Dict(self, original_node:cst.Dict, updated_node: cst.Dict):
            return self.invert_node(original_node,updated_node)
        def leave_FunctionDef(self, original_node:cst.FunctionDef, updated_node: cst.FunctionDef):
            return self.invert_node(original_node,updated_node)