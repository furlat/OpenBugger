from libcst.codemod import CodemodContext, Codemod
from libcst.metadata import MetadataWrapper
from libcst import  CSTNode
import libcst as cst
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.metadata import PositionProvider, CodePosition, CodeRange
import uuid


def is_parent_CodeRange(range_1: CodeRange, range_2: CodeRange) -> bool:
    """Return True if range_1 is a parent of range_2"""
    #for range_1 to be a parent of range_2 it needs to start before the start of range_2 and end after the end of range_2
    # let's check separately the two conditions and then merge them together
    # first condition
    start_before_start = (range_1.start.line < range_2.start.line) or (range_1.start.line == range_2.start.line and range_1.start.column< range_2.start.column)
    end_after_end = (range_1.end.line > range_2.end.line) or (range_1.end.line == range_2.end.line and range_1.end.column >= range_2.end.column)
    parent = start_before_start and end_after_end
    # print("range_1 is a parent of range_2",parent)
    return parent
def is_child_CodeRange(range_1: CodeRange, range_2: CodeRange) -> bool:
    """Return True if range_1 is a child of range_2"""
    # to check if range_1 is a child of range_2 we need to check that range_1 starts after the start of range_2 and ends before the end of range_2
    start_after_start = (range_1.start.line > range_2.start.line) or (range_1.start.line == range_2.start.line and range_1.start.column> range_2.start.column)
    end_before_end = (range_1.end.line < range_2.end.line) or (range_1.end.line == range_2.end.line and range_1.end.column <= range_2.end.column)
    children = start_after_start and end_before_end 
    # print("range_1 is a child of range_2",children)
    return children
def is_equal_Coderange(range_1: CodeRange, range_2: CodeRange) -> bool:
    """Return True if range_1 is equal to range_2"""
    equal = (range_1.start.line == range_2.start.line and range_1.start.column == range_2.start.column) and (range_1.end.line == range_2.end.line and range_1.end.column == range_2.end.column)
    # print("range_1 is equal to range_2",equal)
    return equal
    
def is_modified(node: CSTNode, meta_pos: CodeRange  , context: CodemodContext) -> bool:
    """
    Return True if the node has been modified by a transformer
    
    """
    # we cane use the is_ functions to check if the node has been modified by a transformer by checking if the context contains nodes that are either equal, children or parents of the node
    # print(meta_pos,[x["original_position"] for x in context.scratch.values()])
    equal = any([is_equal_Coderange(meta_pos, x["original_position"]) for x in context.scratch.values()])
    children = any([is_child_CodeRange(meta_pos, x["original_position"]) for x in context.scratch.values()])
    parents = any([is_parent_CodeRange(meta_pos, x["original_position"]) for x in context.scratch.values()])
    return equal or children or parents 


def save_modified(context: CodemodContext, meta_pos: CodeRange, original_node: CSTNode, updated_node:  CSTNode, author: str) -> None:
    """
    Save the modified node in the context.scratch
    """
    context.scratch[meta_pos.start] = {
                "modified": True, 
                "original_position": meta_pos,
                "original_node":original_node ,
                "updated_node":updated_node,
                "author":author
                }
    

class PositionContextUpdater(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext) -> None:
        self.context = context
        #init parent
        super().__init__(self.context)
    def on_visit(self, node: "CSTNode") -> bool:
        return True 
    def update_positions(self, meta_pos: CodePosition) -> None:
            already_modified  = [x for x in self.context.scratch.values() if meta_pos.start== x["original_position"].start]
            # print("already in scratch",[(x["original_position"].start, x["original_position"].end) for x in already_modified]) 
            # print("modified by",[(x["author"]) for x in already_modified])
            modified_keys = [x for x in self.context.scratch.keys() if meta_pos.start== self.context.scratch.get(x)["original_position"].start]
            key = modified_keys[0]
            #compute the delta between the end of the original node and the new one
            delta = meta_pos.end.column - self.context.scratch[key]["original_position"].end.column
            #update the scratch with the new position of the node
            self.context.scratch[key]["original_position"] = meta_pos
            #update the column position of all the nodes in the scratch that are on the same line
            for (k,v) in zip(list(self.context.scratch.keys()),list(self.context.scratch.values())):
                if v["original_position"].start.line == meta_pos.start.line and k.column > key.column:
                    new_start = CodePosition(line=v["original_position"].start.line,column=v["original_position"].start.column+delta)
                    new_end = CodePosition(line=v["original_position"].end.line,column=v["original_position"].end.column+delta)
                    v["original_position"]=CodeRange(start= new_start,end = new_end)
                    self.context.scratch[new_start] = self.context.scratch.pop(k)    
            # print("the delta is",delta)   
    def on_leave(self, node, updated_node):
        meta_pos=self.get_metadata(PositionProvider, node)
        meta_scratch = self.context.scratch.get(meta_pos.start,None)
        if meta_scratch and node.deep_equals(meta_scratch["updated_node"]):
            self.update_positions(meta_pos)
        return updated_node    
    def get_positions(self):
        return self.positions
    

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



