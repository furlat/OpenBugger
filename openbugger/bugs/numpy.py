import random
import uuid
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.metadata import PositionProvider
import libcst as cst
from openbugger.context import is_modified, save_modified
from typing import Optional,List, Dict
from libcst import matchers as m


class NumpyArrayCreationTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        
        if not already_modified:
            if m.matches(original_node, m.Call(func=m.Attribute(value=m.Name("np"), attr=m.Name("array")))):
                updated_node = original_node.with_changes(func=cst.Attribute(value=cst.Name("np"), attr=cst.Name("empty")))
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
            elif m.matches(original_node, m.Call(func=m.Attribute(value=m.Name("numpy"), attr=m.Name("array")))):
                updated_node = original_node.with_changes(func=cst.Attribute(value=cst.Name("numpy"), attr=cst.Name("empty")))
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)

        return updated_node

class NumpyMethodMisuseTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        
        if not already_modified:
            if m.matches(original_node, m.Call(func=m.Attribute(value=m.Name("np"), attr=m.Name("sort")))):
                updated_node = original_node.with_changes(func=cst.Attribute(value=cst.Name("np"), attr=cst.Name("argsort")))
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
            elif m.matches(original_node, m.Call(func=m.Attribute(value=m.Name("numpy"), attr=m.Name("sort")))):
                updated_node = original_node.with_changes(func=cst.Attribute(value=cst.Name("numpy"), attr=cst.Name("argsort")))
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
        return updated_node

class NumpyReshapeMisuseTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)

        # Matching a Call node for reshape function with a list as the first argument
        reshape_matcher = m.Call(
            func=m.Attribute(value=m.Name(), attr=m.Name("reshape")),
            args=[m.AtLeastN(n=1, matcher=m.Arg(m.List()))]
        )

        if not already_modified and m.matches(original_node, reshape_matcher):
            first_arg = updated_node.args[0].value
            elements = first_arg.elements
            first_elem = elements[0].value
            if isinstance(first_elem, cst.Integer):
                first_elem = int(elements[0].value.value)  # Convert libcst.Integer to Python int
                random_increment = random.randint(1, len(elements))  # Generate a random number
                new_first_elem = cst.Element(cst.Integer(str(first_elem + random_increment)))  
                new_elements = [new_first_elem] + list(elements[1:])
                updated_node = updated_node.with_changes(args=[cst.Arg(cst.List(new_elements))])
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)

        return updated_node


class NumpyArangeMisuseTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)

        arange_matcher = m.Call(
            func=m.Attribute(value=m.Name(), attr=m.Name("arange")),
            args=[m.AtLeastN(n=1)]
        )

        if not already_modified and m.matches(original_node, arange_matcher):
            first_arg = updated_node.args[0].value
            if isinstance(first_arg, cst.Integer):
                stop_val = int(first_arg.value)
                decimal_increment = round(random.uniform(0.1, 0.9), 1)  # Generate a random decimal number
                new_stop_val = cst.Arg(cst.Float(str(stop_val + decimal_increment)))  
                updated_node = updated_node.with_changes(args=[new_stop_val] + list(updated_node.args[1:]))
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
        return updated_node


class NumpyAxisMisuseTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)

        # Define the matchers for the numpy functions that we want to target
        func_matchers = [
            m.Attribute(value=m.Name(), attr=m.Name(func_name)) 
            for func_name in ["sum", "mean", "min", "max", "std", "var"]
        ]

        axis_arg_matcher = m.Arg(keyword=m.Name("axis"), value=m.Integer())
        
        if not already_modified and any(m.matches(original_node, m.Call(func=func_matcher)) for func_matcher in func_matchers):
            new_args = []
            for arg in updated_node.args:
                # If the argument matches the "axis" keyword argument with an integer value
                if m.matches(arg, axis_arg_matcher):
                    axis_val = int(arg.value.value)
                    new_arg = cst.Arg(keyword=cst.Name("axis"), value=cst.Integer(str((axis_val + 1) % 2)))
                    new_args.append(new_arg)
                else:
                    new_args.append(arg)

            if new_args != updated_node.args:
                updated_node = updated_node.with_changes(args=new_args)
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)

        return updated_node
