import uuid
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.metadata import PositionProvider
import libcst as cst
import libcst.matchers as m
from openbugger.context import is_modified, save_modified
from typing import Optional,List, Dict

class ForgettingToUpdateVariableTransformer(ContextAwareTransformer):
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
              
        def leave_Assign(self, original_node:cst.Assign, updated_node: cst.Assign) -> None:
            meta_pos = self.get_metadata(PositionProvider, original_node)
            #only updates nodes that are not already in the scratch
            already_modified = is_modified(original_node,meta_pos,self.context)
            if not already_modified:
                updated_node = original_node.with_changes(value=original_node.targets[0].target)
                save_modified(self.context,meta_pos,original_node,updated_node,self.id)
            return updated_node
        
class InfiniteWhileTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
    def mutate(self, tree: cst.Module,reverse: bool = False) -> cst.Module:
            self.reverse=reverse
            return self.transform_module(tree)
    def leave_While(self, original_node: cst.While, updated_node: cst.While) -> None:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        #only updates nodes that are not already in the scratch
        already_modified = is_modified(original_node,meta_pos,self.context)
        if not already_modified: 
            updated_node = cst.While(
                test=cst.Name("True"),
                body=original_node.body
            )
            save_modified(self.context,meta_pos,original_node,updated_node,self.id)
        return updated_node

def gen_OffByKIndexTransformer(k: Optional[int] = 1):
    k=int(k) 
    class OffByKIndexTransformer(ContextAwareTransformer):
        METADATA_DEPENDENCIES = (PositionProvider,)

        def __init__(self, context: CodemodContext):
            super().__init__(context)
            self.k = k
            self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

        def mutate(self, tree: cst.Module,) -> cst.Module:
            return self.transform_module(tree)

        def leave_Index(self, original_node: cst.Index, updated_node: cst.Index) -> cst.Index:
            meta_pos = self.get_metadata(PositionProvider, original_node)
            already_modified = is_modified(original_node, meta_pos, self.context)
                            
            if not already_modified:
                if m.matches(original_node.value, m.Integer()):
                    # extract the value string from the cst.Integer node
                    original_value = original_node.value.value
                    # Convert the value string to an integer, add self.k, and then convert back to a string
                    updated_value = cst.Integer(str(int(original_value) + self.k))
                elif m.matches(original_node.value, m.Name()):
                    updated_value = cst.BinaryOperation(
                        left=original_node.value.deep_clone(),
                        operator=cst.Add(),
                        right=cst.Integer(str(self.k))
                    )
                elif m.matches(original_node.value, m.BinaryOperation()):
                    updated_value = cst.BinaryOperation(
                        left=original_node.value.left.deep_clone(),
                        operator=original_node.value.operator,
                        right=cst.BinaryOperation(
                            left=original_node.value.right,
                            operator=cst.Add(),
                            right=cst.Integer(str(self.k))
                        )
                    )
                else:
                    updated_value = original_node.value
                updated_node = updated_node.with_changes(value=updated_value)
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)

            return updated_node





        def leave_Slice(self, original_node: cst.Slice, updated_node: cst.Slice) -> cst.Slice:
            meta_pos = self.get_metadata(PositionProvider, original_node)
            already_modified = is_modified(original_node, meta_pos, self.context)

            if not already_modified:
                lower = original_node.lower
                upper = original_node.upper

                if m.matches(lower, m.Index(m.Integer())):
                    lower = cst.Index(cst.Integer(int(lower.value.value) + self.k))

                if m.matches(upper, m.Index(m.Integer())):
                    upper = cst.Index(cst.Integer(int(upper.value.value) + self.k))

                updated_node = updated_node.with_changes(lower=lower, upper=upper)
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)

            return updated_node



    return OffByKIndexTransformer

class IncorrectExceptionHandlerTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)
    def leave_ExceptHandler(self, original_node: cst.ExceptHandler, updated_node: cst.ExceptHandler) -> cst.ExceptHandler:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node,meta_pos,self.context)
        if not already_modified:
            updated_node = original_node.with_changes(type=None)
            save_modified(self.context,meta_pos,original_node,updated_node,self.id)
        return updated_node
    
class MissingArgumentTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        self.reverse = reverse
        return self.transform_module(tree)
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node,meta_pos,self.context)
        if not already_modified and original_node.args:
            updated_node = original_node.with_changes(args=original_node.args[:-1])
            save_modified(self.context,meta_pos,original_node,updated_node,self.id)
        return updated_node
    

class ReturningEarlyTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        self.reverse = reverse
        return self.transform_module(tree)
    def leave_Return(self, original_node: cst.Return, updated_node: cst.Return) -> cst.Return:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node,meta_pos,self.context)
        if not already_modified:
            updated_node = cst.Return(value=None)
            save_modified(self.context,meta_pos,original_node,updated_node,self.id)
        return updated_node