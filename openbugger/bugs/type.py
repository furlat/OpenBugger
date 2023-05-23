import random
import uuid
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.metadata import PositionProvider
import libcst as cst
from openbugger.context import is_modified, save_modified
from typing import Optional,List, Dict
from libcst import matchers as m


class IncorrectTypeTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        self.type_transformations = {
            cst.Integer: cst.SimpleString,
            cst.SimpleString: cst.Integer,
            cst.Float: cst.Integer,
        }

    def leave_Integer(self, original_node: cst.Integer, updated_node: cst.Integer) -> cst.CSTNode:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        if m.matches(updated_node, m.Integer()) and not already_modified:
            updated_node = cst.SimpleString(f'"{original_node.value}"')
            save_modified(self.context, meta_pos, original_node, updated_node, self.id)
            return updated_node
        return updated_node

    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString) -> cst.CSTNode:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        if m.matches(updated_node, m.SimpleString()) and not already_modified:
            # Removing the quotes around the string before converting to integer
            value = original_node.value.strip('\"\'')
            try:
                int_value = int(value)
                updated_node = cst.Integer(str(int_value))
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
                return updated_node
            except ValueError:
                # If the string cannot be converted to an integer, keep it as a string
                return updated_node
        return updated_node

    def leave_Float(self, original_node: cst.Float, updated_node: cst.Float) -> cst.CSTNode:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        if m.matches(updated_node, m.Float()) and not already_modified:
            updated_node = cst.Integer(str(int(float(str(original_node.value)))))
            save_modified(self.context, meta_pos, original_node, updated_node, self.id)
            return updated_node
        return updated_node

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

class NonExistingMethodTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    # Define a mapping from existing methods to non-existing methods
    METHOD_TRANSFORM_MAP: Dict[str, str] = {
        "append": "update",  # list to dictionary
        "add": "extend",  # set to list
        "update": "add",  # dictionary to set
        "extend": "append"  # list to list
    }

    def __init__(self, context):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        self.mutated = False

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        if m.matches(updated_node, m.Call(func=m.Attribute())):
            attribute = updated_node.func
            if isinstance(attribute.attr, cst.Name):
                attr_name = attribute.attr.value
                if attr_name in self.METHOD_TRANSFORM_MAP:
                    updated_node = updated_node.with_changes(func=attribute.with_changes(attr=cst.Name(self.METHOD_TRANSFORM_MAP[attr_name])))
                    save_modified(self.context, self.get_metadata(PositionProvider, original_node), original_node, updated_node, self.id)
        return updated_node

class SwapForTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

    def leave_For(self, original_node: cst.For, updated_node: cst.For) -> cst.BaseSmallStatement:
        # For to While
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)

        if not already_modified:
            # Syntax for for loop is 'for target in iterable'
            target = original_node.target
            iterable = original_node.iter
            # While loops are structured 'while condition'
            # For the condition we can use an iterator, a workaround could be using `iter` function
            condition = cst.Call(func=cst.Name("next"), args=[cst.Arg(iterable)])
            while_node = cst.While(test=condition, body=updated_node.body)
            save_modified(self.context, meta_pos, original_node, while_node, self.id)
            return while_node

        return updated_node

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)