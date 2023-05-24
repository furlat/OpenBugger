from libcst.codemod import CodemodContext, Codemod
from libcst import  Module
from typing import List

import libcst as cst
from libcst.codemod import CodemodContext, ContextAwareTransformer, ContextAwareVisitor
from libcst.metadata import BatchableMetadataProvider, PositionProvider, CodePosition, CodeRange
import libcst.matchers as m
import uuid

from openbugger.context import is_modified, save_modified, PositionContextUpdater

from dataclasses import fields
from typing import Sequence

from libcst._nodes.base import CSTNode

def deep_equals_with_print(a: object, b: object) -> bool:
    if isinstance(a, CSTNode) and isinstance(b, CSTNode):
        return deep_equals_cst_node_with_print(a, b)
    elif (
        isinstance(a, Sequence)
        and not isinstance(a, (str, bytes))
        and isinstance(b, Sequence)
        and not isinstance(b, (str, bytes))
    ):
        return _deep_equals_sequence(a, b)
    else:
        return a == b


def _deep_equals_sequence(a: Sequence[object], b: Sequence[object]) -> bool:
    if a is b:  # short-circuit
        return True
    if len(a) != len(b):
        print(f"Sequence length mismatch: {len(a)} != {len(b)}")
        return False
    return all(deep_equals_with_print(a_el, b_el) for (a_el, b_el) in zip(a, b))


def deep_equals_cst_node_with_print(a: "CSTNode", b: "CSTNode") -> bool:
    if type(a) is not type(b):
        print(f"Type mismatch: {type(a)} != {type(b)}")
        print(f"Node A: {a}")
        print(f"Node B: {b}")
        return False
    if a is b:  # short-circuit
        return True
    # Ignore metadata and other hidden fields
    for field in (f for f in fields(a) if f.compare is True):
        a_value = getattr(a, field.name)
        b_value = getattr(b, field.name)
        if not deep_equals_with_print(a_value, b_value):  # Changed this line
            print(f"Value mismatch in field '{field.name}': {a_value} != {b_value}")  # Added this line for debugging
            return False
    return True


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
                diff = deep_equals_with_print(self.original,self.clean)
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
                # print("reverting to old node",meta_pos.start, meta_pos.end)
                # print("current node",original_node)
                # print("reverting to node",updated_node)
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
        def leave_Integer(self, original_node:cst.Integer, updated_node: cst.Integer):
            return self.invert_node(original_node,updated_node)
        def leave_SimpleString(self, original_node:cst.SimpleString, updated_node: cst.SimpleString):
            return self.invert_node(original_node,updated_node)
        def leave_Float(self, original_node:cst.Float, updated_node: cst.Float):
            return self.invert_node(original_node,updated_node)
        def leave_Attribute(self, original_node:cst.Attribute, updated_node: cst.Attribute):
            return self.invert_node(original_node,updated_node)
        