from libcst import (Equal, GreaterThanEqual, LessThan, GreaterThan, 
                    LessThanEqual, NotEqual, NotIn, In, Is, IsNot, Not, And, Or, Match)
import uuid
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.metadata import PositionProvider
import libcst as cst
from openbugger.context import is_modified, save_modified
from typing import Optional,List, Dict
import random

def gen_ComparisonTargetTransfomer(op1: Optional[str] = None, op2:Optional[str] = None):
    """ A factory function that returns a ComparisonTargetTransformer that replaces all the occurences of op1 with op2"""
    #mapping from string to libcst comparisontarget operator class
    #if op1 or op2 are None then they will be replaced with a random operator
    op1= op1 or random.choice(list(str2op.keys()))
    #sample random op2 different from op1
    op2 = op2 or random.choice(list(set(str2op.keys()) - set(op1)))
    str2op = dict([
    ('==', Equal),
    ('>=', GreaterThanEqual),
    ('>', GreaterThan),
    ('<', LessThan),
    ('=<', LessThanEqual),
    ('!=', NotEqual),
    ('not in', NotIn),
    ('in', In),
    ('is', Is),
    ('is not', IsNot),
    ('not', Not),
    ('and', And),
    ('or', Or),
    ('or', Or),])

    #check if the op1 and op2 are valid they can either be a string or a libcst comparisontarget operator class
    if op1 in str2op.keys():
        op1 = str2op[op1]
    elif op1 not in str2op.values():
        raise ValueError("op1 must be a string or a class") 
    if op2 in str2op.keys():
        op2 = str2op[op2]
    elif op2 not in str2op.values():
        raise ValueError("op2 must be a string or a class")
            
    class ComparisonTargetTransformer(ContextAwareTransformer):
        """ A transformer that replaces all the occurences of ComparisonTarget op1 with op2"""
        METADATA_DEPENDENCIES = (PositionProvider, )
        def __init__(
            self,
            context: CodemodContext):
            self.op1 = op1
            self.op2 = op2
            super().__init__(context)
            self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        def transform_module_impl(self, tree: cst.Module) -> cst.Module:
            return tree.visit(self)
        def mutate(self, tree: cst.Module,reverse: bool = False) -> cst.Module:
            return self.transform_module(tree)
              
        def leave_ComparisonTarget(self, original_node:cst.ComparisonTarget, updated_node: cst.ComparisonTarget) -> None:
            meta_pos = self.get_metadata(PositionProvider, original_node)
            already_modified = is_modified(original_node,meta_pos,self.context)
            if not already_modified and original_node.operator.__class__ == self.op1: 
                updated_node = original_node.with_changes(operator=self.op2()) # OP2
                save_modified(self.context,meta_pos,original_node,updated_node,self.id)
            return updated_node
            
        def __repr__(self):
            return super().__repr__(self) + ':' + op1.__name__ +':' + op2.__name__
    
    return ComparisonTargetTransformer  



class ComparisonSwapTransformer(ContextAwareTransformer):
    """ Swap the left and right side of a comparison, if there are moe than one comparison it swaps the first one"""    
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
    def mutate(self, tree: cst.Module,) -> cst.Module:
            return self.transform_module(tree)
    

    def leave_Comparison(self, original_node: cst.Comparison, updated_node: cst.Comparison) -> None:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        #only updates nodes that are not already in the scratch
        already_modified = is_modified(original_node,meta_pos,self.context)
        
        comparisons = original_node.comparisons
        
        # only update the first comparison
        if not already_modified and len(comparisons) > 0:
            left = original_node.left
            lpar = original_node.lpar
            rpar = original_node.rpar
            first_comparison = comparisons[0]
            new_left = first_comparison.comparator
            first_comparison = cst.ComparisonTarget(
                operator=first_comparison.operator, 
                comparator=left
            )
            
            comparisons = list(comparisons)
            comparisons[0] = first_comparison
            comparisons = tuple(comparisons)
            updated_node = cst.Comparison(
                left=new_left,
                comparisons=comparisons,
                lpar=lpar,
                rpar=rpar
            )
            save_modified(self.context,meta_pos,original_node,updated_node,self.id)
        return updated_node        