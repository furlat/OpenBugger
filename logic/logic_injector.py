import random
import re


class LogicInjector:
    def __init__(self, errors):
        self.errors = errors

    def inject(self, script, error_type):  # noqa:
        if error_type == "incorrect_comparison_operator":
            return incorrect_comparison_operator(script, self.errors)
        elif error_type == "forgetting_to_update_variable":
            return forgetting_to_update_variable(script, self.errors)
        elif error_type == "infinite_loop":
            return infinite_loop(script, self.errors)
        elif error_type == "off_by_one_error":
            return off_by_one_error(script, self.errors)
        elif error_type == "incorrect_function_call":
            return incorrect_function_call(script, self.errors)
        elif error_type == "incorrect_return_value":
            return incorrect_return_value(script, self.errors)
        # elif error_type == "incorrect_boolean_operator":
        #     return logic_bugs.incorrect_boolean_operator(script,self.errors)
        elif error_type == "using_wrong_type_of_loop":
            return using_wrong_type_of_loop(script, self.errors)
        elif error_type == "using_loop_variable_outside_loop":
            return using_loop_variable_outside_loop(script, self.errors)
        elif error_type == "using_variable_before_assignment":
            return using_variable_before_assignment(script, self.errors)
        elif error_type == "using_wrong_variable_scope":
            return using_wrong_variable_scope(script, self.errors)
        elif error_type == "incorrect_use_of_exception_handling":
            return incorrect_use_of_exception_handling(script, self.errors)

        else:
            raise ValueError("Invalid error type")


class LogicBug:
    def __init__(self):
        # define lists of different types of syntax errors that can be injected

        self.errors = {
            "incorrect_comparison_operator": (
                ["==", "!=", "<", "<=", ">", ">="],
                [r"\s*([!<=>]{1,2})\s*"],
            ),
            "forgotten_variable_update": (
                ["+=", "-=", "=", "/=", "%="],
                [r"[a-zA-Z]+\s*=\s*[a-zA-Z0-9]+"],
            ),
            "infinite_loop": (["while", "for"], [r"while\s*[a-zA-Z0-9_\s]+:"]),
            "off_by_one_error": (["index", "slice"], [r"[[0-9]+]|[[0-9]+:[0-9]+]"]),
            "incorrect_function_call": (
                ["function", "arguments"],
                [r"[a-zA-Z_]+\s*\([a-zA-Z0-9_\s,]*\)"],
            ),
            "incorrect_return_value": (["return"], [r"return\s[a-zA-Z0-9_\s]+"]),
            # "incorrect_boolean_operator": (["and", "or"], [r"\s(and|or)\s*"]),
            "incorrect_use_of_boolean_operators": (
                ["if", "else"],
                [r"\s*(if|else)\s*"],
            ),
            "incorrect_use_of_ternary_operator": (["if", "else"], [r"\s*(if|else)\s*"]),
            "using_wrong_type_of_loop": (
                ["for"],
                [r"for\s*[a-zA-Z0-9_\s]+\sin\s[a-zA-Z0-9_\s()]+:"],
            ),
            "using_loop_variable_outside_loop": (
                ["for"],
                [r"for\s*[a-zA-Z0-9_\s]+\sin\s[a-zA-Z0-9_\s()]+:"],
            ),
            "using_variable_before_assignment": ([], [r"[a-zA-Z]+\s*=\s*[a-zA-Z0-9]+"]),
            "using_wrong_variable_scope": (
                ["local", "global", "nonlocal"],
                [r"(local|global|nonlocal)\s+[a-zA-Z0-9_\s]+"],
            ),
            "incorrect_use_of_exception_handling": (
                ["try", "except"],
                [r"(try|except)\s*[a-zA-Z0-9_\s:]+"],
            ),
        }
        self.injector = LogicInjector(self.errors)

        self.severity_mapping = {
            "easy": [
                "incorrect_comparison_operator",
                "forgotten_variable_update",
                "infinite_loop",
            ],
            "medium": [
                "off_by_one_error",
                "incorrect_function_call",
                "incorrect_return_value",
                "incorrect_use_of_boolean_operators",
                "incorrect_use_of_ternary_operator",
            ],
            "hard": [
                "using_wrong_type_of_loop",
                "using_loop_variable_outside_loop",
                "using_variable_before_assignment",
                "using_wrong_variable_scope",
                "incorrect_use_of_exception_handling",
            ],
        }

    def count_injectables(self, script, error_types=None):
        error_counts = {}
        if error_types is None:
            error_types = list(self.errors.keys())
        for error_type, (chars, pattern) in list(self.errors.items()):
            count = 0
            if error_type in error_types:
                count += len(re.findall(pattern[0], script))
            error_counts[error_type] = count
        return error_counts

    def inject(self, script, severity=None, error_type=None, num_errors=1):
        if severity:
            if severity not in self.severity_mapping:
                raise ValueError("Invalid severity level")
            error_list = self.severity_mapping[severity]
        elif error_type:
            if error_type not in self.errors:
                raise ValueError("Invalid error type")
            error_list = [error_type]
        else:
            raise ValueError("Either severity or error_type must be specified")
        # print(self.errors.items())
        # count the number of instances of each error type in the script
        error_counts = self.count_injectables(script, error_types=error_list)
        # check if there are enough instances of the error type to inject the errors
        if sum(error_counts.values()) >= num_errors:
            modified_script = script
            errors_injected = 0
            counter = 0
            while errors_injected < num_errors and counter < 100 * num_errors:
                # choose a random error from the selected list

                random_error = random.choice(error_list)

                if error_counts[random_error] > 0:
                    modified_script = self.injector.inject(
                        modified_script, error_type=random_error
                    )
                    errors_injected += 1
                    error_counts[random_error] -= 1
                counter += 1
            return modified_script, errors_injected, counter
        else:
            raise ValueError(
                "Not enough instances of the required error type in the script"
            )


def incorrect_comparison_operator(script, errors_dict):
    # Choose a random comparison operator in the script (e.g., "==", ">=", "<=") and replace it with a different comparison operator.
    comparison_operators, comparison_regex = errors_dict[
        "incorrect_comparison_operator"
    ]
    curr_op = random.choice(comparison_operators)
    comparison_operators.remove(curr_op)
    new_op = random.choice(comparison_operators)
    return script.replace(curr_op, new_op, 1)


def forgetting_to_update_variable(script, errors_dict):
    # Choose a random assignment statement in the script (e.g., "x = 5") and replace the right-hand side with the same variable on the left-hand side (e.g., "x = x").
    assignment_operators, assignment_regex = errors_dict["forgotten_variable_update"]
    assignment_pattern = assignment_regex[0]
    assignments = re.findall(assignment_pattern, script)
    if assignments:
        assignment = random.choice(assignments)
        var_name = assignment.split("=")[0].strip()
        modified_assignment = f"{var_name} = {var_name}"
        return script.replace(assignment, modified_assignment, 1)
    else:
        raise ValueError("No assignment statements found in script")


def infinite_loop(script, errors_dict):
    # Choose a random "while" or "for" loop in the script and remove the loop condition (e.g., "while True:" or "for i in range(10):").
    while_pattern = errors_dict["infinite_loop"][1][0]
    for_pattern = errors_dict["infinite_loop"][1][0]
    while_loops = re.findall(while_pattern, script)
    for_loops = re.findall(for_pattern, script)
    if while_loops:
        loop = random.choice(while_loops)
        modified_loop = loop.replace(loop.split(":")[0], "while True", 1)
        return script.replace(loop, modified_loop, 1)
    elif for_loops:
        loop = random.choice(for_loops)
        modified_loop = loop.replace(loop.split(":")[0], "for i in range(10)", 1)
        return script.replace(loop, modified_loop, 1)
    else:
        raise ValueError("No while or for loops found in script")


def off_by_one_error(script, errors_dict):
    # Choose a random list index or slice in the script (e.g., "my_list[3]") and add or subtract 1 from the index or slice (e.g., "my_list[4]" or "my_list[2:4]").
    # Find all instances of list indexes or slices in the script
    index_pattern = errors_dict["off_by_one_error"][1][0]
    indexes = re.findall(index_pattern, script)
    if indexes:
        # Choose a random list index and add or subtract 1
        index = random.choice(indexes)
        index_val = int(index[1:-1])
        if random.random() < 0.5:
            modified_index = f"[{index_val - 1}]"
        else:
            modified_index = f"[{index_val + 1}]"
        script = script.replace(index, modified_index, 1)
    else:
        # Choose a random list slice and add or subtract 1 from the start or end index
        slice_pattern = errors_dict["off_by_one_error"][1][0]
        slices = re.findall(slice_pattern, script)
        slice_ = random.choice(slices)
        slice_start, slice_end = slice_[1:-1].split(":")
        slice_start, slice_end = int(slice_start), int(slice_end)
        if random.random() < 0.5:
            if random.random() < 0.5:
                slice_start -= 1
            else:
                slice_end -= 1
        else:
            if random.random() < 0.5:
                slice_start += 1
            else:
                slice_end += 1
        modified_slice = f"[{slice_start}:{slice_end}]"
        script = script.replace(slice_, modified_slice, 1)
    return script


def incorrect_function_call(script, errors_dict):
    # Choose a random function call in the script (e.g., "my_function()") and change the number or order of the arguments (e.g., "my_function(5, True)").
    function_pattern = errors_dict["incorrect_function_call"][1][0]
    functions = re.findall(function_pattern, script)
    if functions:
        # Choose a random function and modify its arguments
        function = random.choice(functions)
        function_name = function.split("(")[0]
        args = function.split("(")[1]
        if args[-1] == ")":
            args = args[:-1]
        if args:
            # Split the current arguments into a list
            curr_args = [arg.strip() for arg in args.split(",")]
            # Choose a random number of arguments to remove or add
            num_changes = random.randint(-len(curr_args), len(curr_args))
            for _ in range(num_changes):
                if len(curr_args) == 0:
                    # Add a random argument
                    curr_args.append(
                        random.choice(["True", "False", "5", "10", '"hello"'])
                    )
                else:
                    # Remove a random argument or add a random argument
                    if random.random() < 0.5:
                        curr_args.pop(random.randint(0, len(curr_args) - 1))
                    else:
                        curr_args.append(
                            random.choice(["True", "False", "5", "10", '"hello"'])
                        )
            # Rebuild the modified function call with the modified argument list
            modified_function = f"{function_name}({', '.join(curr_args)})"
            script = script.replace(function, modified_function, 1)
        else:
            # Add a random number of arguments to the function call
            num_args = random.randint(1, 3)
            new_args = ", ".join(
                [
                    random.choice(["True", "False", "5", "10", '"hello"'])
                    for _ in range(num_args)
                ]
            )
            modified_function = f"{function_name}({new_args})"
            script = script.replace(function, modified_function, 1)
    else:
        raise ValueError("No function calls found in script")
    return script


def incorrect_return_value(script, errors_dict):
    # Choose a random return statement in the script (e.g., "return x + y") and replace the return value with a different value (e.g., "return x - y").
    return_pattern = errors_dict["incorrect_return_value"][1][0]
    returns = re.findall(return_pattern, script)
    if returns:
        return_stmt = random.choice(returns)
        return_value = return_stmt.split("return")[1].strip()
        if " " in return_value:
            modified_return_value = return_value.replace(" ", " - ", 1)
        else:
            modified_return_value = "5"
        modified_return_stmt = f"return {modified_return_value}"
        return script.replace(return_stmt, modified_return_stmt, 1)
    else:
        raise ValueError("No return statements found in script")


# def incorrect_boolean_operator(script, errors_dict):
#     # Choose a random boolean operator in the script (e.g., "and", "or") and replace it with the other boolean operator.
#     boolean_operators = errors_dict['incorrect_boolean_operator'][0]
#     pattern = errors_dict['incorrect_boolean_operator'][1][0]
#     boolean_ops = re.findall(pattern, script)
#     if boolean_ops:
#         curr_op = random.choice(boolean_ops)
#         boolean_operators.remove(curr_op)
#         new_op = boolean_operators[0]
#         return script.replace(curr_op, new_op, 1)
#     else:
#         raise ValueError("No boolean operators found in script")


def incorrect_use_of_ternary_operator(script, errors_dict):
    # Choose a random "if" or "else" in the script and replace it with the other keyword (e.g., "if" becomes "else" or vice versa).
    if_pattern = errors_dict["incorrect_use_of_ternary_operator"][1][0]
    ifs = re.findall(if_pattern, script)
    if ifs:
        if_ = random.choice(ifs)
        if if_ == "if":
            modified_if = "else"
        else:
            modified_if = "if"
        return script.replace(if_, modified_if, 1)
    else:
        raise ValueError("No if or else statements found in script")


def using_wrong_type_of_loop(script, errors_dict):
    # Choose a random "for" loop in the script and change the loop variable type from iterating over a list to iterating over a range or vice versa (e.g., "for i in range(10):" or "for i in my_list:").
    for_pattern = errors_dict["using_wrong_type_of_loop"][1][0]
    for_loops = re.findall(for_pattern, script)
    if for_loops:
        loop = random.choice(for_loops)
        loop_var = loop.split("in")[0].split()[-1]
        if "range" in loop:
            modified_loop = loop.replace("range", "my_list", 1)
        else:
            modified_loop = loop.replace("in my_list", "in range(10)", 1)
        script = script.replace(loop, modified_loop, 1)
        # Add a list or range to the script if not already present
        if "my_list" in modified_loop:
            if "my_list" not in script:
                script += f"\nmy_list = [{loop_var}, {loop_var}]"
        elif "range" in modified_loop:
            if "range" not in script:
                script += "\nrange = range"
        return script
    else:
        raise ValueError("No for loops found in script")


def using_loop_variable_outside_loop(script, errors_dict):
    # Choose a random "for" loop in the script and use the loop variable outside of the loop.
    for_pattern = errors_dict["using_loop_variable_outside_loop"][1][0]
    for_loops = re.findall(for_pattern, script)
    if for_loops:
        loop = random.choice(for_loops)
        loop_parts = loop.split(" ")
        loop_var = loop_parts[1]
        modified_script = script.replace(loop, "", 1)
        modified_script += f"\nprint({loop_var})"
        return modified_script
    else:
        raise ValueError("No for loops found in script")


def using_variable_before_assignment(script, errors_dict):
    # Choose a random variable in the script and use it before it is assigned a value.
    # Find all instances of assignment statements in the script
    assignment_regex = errors_dict["using_variable_before_assignment"][1][0]
    assignment_pattern = assignment_regex[0]
    assignments = re.findall(assignment_pattern, script)
    if assignments:
        # Choose a random assignment statement and use the left-hand side variable before the assignment
        assignment = random.choice(assignments)
        var_name = assignment.split("=")[0].strip()
        modified_script = script.replace(assignment, "", 1)
        modified_script = f"print({var_name})\n{modified_script}"
        return modified_script
    else:
        raise ValueError("No assignment statements found in script")


def using_wrong_variable_scope(script, errors_dict):
    # Choose a random variable in the script and change its scope (e.g., "global", "nonlocal", "local").
    # Find all instances of assignment statements in the script
    assignment_regex = errors_dict["using_wrong_variable_scope"][1][0]
    assignments = re.findall(assignment_regex, script)
    if assignments:
        # Choose a random assignment statement and change the scope of the left-hand side variable
        assignment = random.choice(assignments)
        scopes = ["global", "nonlocal", "local", "\n"]
        # remove the current scope from the list of scopes
        scopes = [x for x in scopes if x not in assignment]
        scope = random.choice(scopes)
        modified_script = script.replace(str(assignment), scope)
        return modified_script
    else:
        raise ValueError("No assignment statements found in script")


def incorrect_use_of_exception_handling(script, errors_dict):
    # Choose a random "try" or "except" block in the script and remove it or
    # change the exception type.
    # Find all instances of "try" or "except" blocks in the script
    try_pattern = errors_dict["incorrect_use_of_exception_handling"][1][0]
    except_pattern = errors_dict["incorrect_use_of_exception_handling"][1][0]
    tries = re.findall(try_pattern, script)
    excepts = re.findall(except_pattern, script)
    if tries:
        # Choose a random "try" block and remove it
        block = random.choice(tries)
        script = script.replace(block, "", 1)
    elif excepts:
        # Choose a random "except" block and change the exception type
        block = random.choice(excepts)
        exception_type = block.split(" ")[1]
        if exception_type in ["Exception", "BaseException"]:
            new_exception_type = random.choice(["ValueError", "TypeError", "KeyError"])
        else:
            new_exception_type = "Exception"
        modified_block = block.replace(exception_type, new_exception_type, 1)
        script = script.replace(block, modified_block, 1)
    else:
        raise ValueError("No try or except blocks found in script")


# def incorrect_use_of_builtin_function(script, errors_dict):
#     # Choose a random built-in function in the script and change the name of
# the function or the number or order of the arguments.
#     # Find all instances of built-in functions in the script
#     func_pattern = errors_dict['incorrect_use_of_builtin_function'][1][0]
#     funcs = re.findall(func_pattern, script)
#     if funcs:
#         # Choose a random built-in function and change the name or arguments
#         func = random.choice(funcs)
#         func_name = func.split("(")[0]
#         func_args = func.split("(")[1]
#         if func_args[-1] == ")":
#             func_args = func_args[:-1]

#         if random.random() < 0.5:
#             # Change the name of the function
#             new_func_name = random.choice(["print", "len", "range"])
#             modified_func = f"{new_func_name}({func_args})"
#         else:
#             # Change the number or order of the arguments
#             if "," in func_args:
#                 # Split the arguments into a list
#                 arg_list = func_args.split(",")
#                 # Remove a random argument
#                 removed_arg = random.choice(arg_list)
#                 arg_list.remove(removed_arg)
#                 # Rebuild the argument string with the removed argument
#                 modified_args = ",".join(arg_list)
#             else:
#                 # Add an extra argument
#                 modified_args = f"{func_args}, 'extra_arg'"
#             modified_func = f"{func_name}({modified_args})"
#         script = script.replace(func, modified_func, 1)
#     return script
