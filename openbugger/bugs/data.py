import random
import uuid
from libcst.codemod import CodemodContext, ContextAwareTransformer
from libcst.metadata import PositionProvider
import libcst as cst
from openbugger.context import is_modified, save_modified
from typing import Optional,List, Dict

def to_int(s):
    try:
        if s.startswith('0x'):
            return int(s, 16)
        else:
            return int(s)
    except ValueError:
        return None

DEFAULT_VALUES = {
    int: [1, 2, 3, 4, 5],
    str: ['foo', 'bar', 'baz'],
    list: [[1, 2, 3], ['a', 'b', 'c'], []],
    dict: [{'key': 'value'}, {}, {'num': 1, 'bool': False}],
    bool: [True, False],
    None: [None]
}

from libcst import matchers
from libcst.metadata import ParentNodeProvider


class IncorrectVariableInitializationTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider, ParentNodeProvider)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        if not already_modified:
            if matchers.matches(updated_node.value, matchers.SimpleString()):
                old_value = updated_node.value.value
                old_value_type = str
            elif matchers.matches(updated_node.value, matchers.Integer()):
                old_value = to_int(updated_node.value.value)
                old_value_type = int
            elif matchers.matches(updated_node.value, matchers.Float()):
                old_value = float(updated_node.value.value)
                old_value_type = float
            elif matchers.matches(updated_node.value, matchers.Name()):
                old_value = updated_node.value.value
                if old_value == "True" or old_value == "False":
                    old_value_type = bool
                elif old_value == "None":
                    old_value_type = type(None)
                else:
                    return updated_node
            else:
                return updated_node

            new_value = random.choice(DEFAULT_VALUES.get(old_value_type, [0]))
            
            if old_value_type == str:
                new_value = f'"{new_value}"'

            updated_node = original_node.with_changes(value=cst.parse_expression(str(new_value)))
            save_modified(self.context, meta_pos, original_node, updated_node, self.id)
        return updated_node

    
    def leave_List(self, original_node: cst.List, updated_node: cst.List) -> cst.List:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node,meta_pos,self.context)
        
        parent_node = self.get_metadata(ParentNodeProvider, original_node)
        if isinstance(parent_node, cst.Assign):
            if not already_modified and len(updated_node.elements) > 0:
                idx = random.randint(0, len(updated_node.elements)-1)
                new_value = random.choice(DEFAULT_VALUES.get(int, [0]))
                updated_elements = list(updated_node.elements)
                updated_elements[idx] = updated_elements[idx].with_changes(value=cst.Integer(str(new_value)))
                updated_node = updated_node.with_changes(elements=tuple(updated_elements))
                save_modified(self.context,meta_pos,original_node,updated_node,self.id)
        return updated_node
    
    def leave_Dict(self, original_node: cst.Dict, updated_node: cst.Dict) -> cst.Dict:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)

        parent_node = self.get_metadata(ParentNodeProvider, original_node)
        if isinstance(parent_node, cst.Assign):
            if not already_modified and len(updated_node.elements) > 0:
                idx = random.randint(0, len(updated_node.elements) - 1)
                old_element = updated_node.elements[idx]

                if isinstance(old_element, cst.DictElement):
                    new_value = random.choice(DEFAULT_VALUES.get(str, ["foo", "bar", "baz"]))
                    updated_element = old_element.with_changes(value=cst.SimpleString(f'"{new_value}"'))

                    updated_elements = list(updated_node.elements)
                    updated_elements[idx] = updated_element
                    updated_node = updated_node.with_changes(elements=tuple(updated_elements))
                    save_modified(self.context, meta_pos, original_node, updated_node, self.id)
        return updated_node


class VariableNameTypoTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        self.seen_variables = set()

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        return self.transform_module(tree)

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)

        if not already_modified:
            targets = []
            for target in original_node.targets:
                if isinstance(target.target, cst.Name):
                    var_name = target.target.value
                    self.seen_variables.add(var_name)
                    extra_character = random.choice(list(self.seen_variables)) if self.seen_variables else ''
                    new_name = cst.Name(var_name + extra_character)
                    target = target.with_changes(target=new_name)
                targets.append(target)
            updated_node = original_node.with_changes(targets=targets)
            save_modified(self.context, meta_pos, original_node, updated_node, self.id)
        return updated_node
    

class MutableDefaultArgumentTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        self.used_variables = set()
        self.first_pass = True

    def visit_Name(self, node: cst.Name) -> Optional[bool]:
        # During the first pass, record all the variable names used in the module
        if self.first_pass:
            self.used_variables.add(node.value)
        return None

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        # Only modify function definitions during the second pass
        if not self.first_pass and self.used_variables and not already_modified:
            # Only replace the last variable in the parameters list
            variable_to_replace = updated_node.params.params[-1].name.value if updated_node.params.params else None
            if variable_to_replace and variable_to_replace in self.used_variables:
                self.used_variables.remove(variable_to_replace)
                
                # Build new parameters, replacing the last variable with a mutable default argument
                new_params_list = list(updated_node.params.params[:-1])
                new_params_list.append(cst.Param(name=cst.Name(variable_to_replace), default=cst.List([])))
                new_params = cst.Parameters(params=tuple(new_params_list))

                
                # Build a new function body that modifies the mutable default argument
                assignment = cst.parse_statement(f"{variable_to_replace}.append(1)")

                # If the body is non-empty, insert the assignment before the last statement. 
                # Otherwise, add the assignment as the only statement.
                if updated_node.body.body:
                    new_body = cst.IndentedBlock(
                        body=list(updated_node.body.body[:-1]) + [assignment] + [updated_node.body.body[-1]]
                    )
                else:
                    new_body = cst.IndentedBlock(
                        body=[assignment]
                    )

                # Return the updated function definition
                updated_node = updated_node.with_changes(params=new_params, body=new_body)
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
                return updated_node
        return updated_node




    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        # First pass: collect variable names
        self.first_pass = True
        self.transform_module(tree)
        # Second pass: introduce bugs
        self.first_pass = False
        return self.transform_module(tree)


class UseBeforeDefinitionTransformer(ContextAwareTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:4]}"
        self.first_pass = True
        self.function_scopes: Dict[str, List[str]] = {}
        self.current_function = None

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.current_function = node.name.value
        if self.first_pass:
            self.function_scopes[self.current_function] = []

    def visit_Param(self, node: cst.Param) -> None:
        if self.first_pass:
            self.function_scopes[self.current_function].append(node.name.value)

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        meta_pos = self.get_metadata(PositionProvider, original_node)
        already_modified = is_modified(original_node, meta_pos, self.context)
        if not self.first_pass and not already_modified:
            local_vars = self.function_scopes[updated_node.name.value]
            if len(local_vars) >= 2:
                # Choose two variable names randomly
                var1, var2 = random.sample(local_vars, 2)
                new_var_name = var1 + var2
                
                # Create an expression with an undefined variable before its definition.
                new_statement = cst.parse_statement(f"{new_var_name} = {var1} + 1")
                new_body = cst.IndentedBlock(
                    body=[new_statement] + list(updated_node.body.body)
                )
                updated_node = updated_node.with_changes(body=new_body)
                save_modified(self.context, meta_pos, original_node, updated_node, self.id)
                return updated_node
        return updated_node

    def mutate(self, tree: cst.Module, reverse: bool = False) -> cst.Module:
        self.first_pass = True
        self.transform_module(tree)  # First pass: collect function parameters
        self.first_pass = False
        return self.transform_module(tree)  # Second pass: introduce bugs
