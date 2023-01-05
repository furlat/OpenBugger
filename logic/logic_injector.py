import random
import re
import logic.logic_bugs as logic_bugs
class LogicInjector:
    def __init__(self, errors):
        self.errors = errors
    def inject(self,script, error_type):
        if error_type == "incorrect_comparison_operator":
            return logic_bugs.incorrect_comparison_operator(script,self.errors)        
        elif error_type == "forgetting_to_update_variable":
            return logic_bugs.forgetting_to_update_variable(script,self.errors)         
        elif error_type == "infinite_loop":
            return logic_bugs.infinite_loop(script,self.errors)           
        elif error_type == "off_by_one_error":
            return logic_bugs.off_by_one_error(script,self.errors)
        elif error_type == "incorrect_function_call":
            return logic_bugs.incorrect_function_call(script,self.errors)
        elif error_type == "incorrect_return_value":
            return logic_bugs.incorrect_return_value(script,self.errors)
        elif error_type == "incorrect_boolean_operator":
            return logic_bugs.incorrect_boolean_operator(script,self.errors)
        elif error_type == "using_wrong_type_of_loop":
            return logic_bugs.using_wrong_type_of_loop(script,self.errors)
        elif error_type == "using_loop_variable_outside_loop":
            return logic_bugs.using_loop_variable_outside_loop(script,self.errors)
        elif error_type == "using_variable_before_assignment":
            return logic_bugs.using_variable_before_assignment(script,self.errors)
        elif error_type == "using_wrong_variable_scope":
            return logic_bugs.using_wrong_variable_scope(script,self.errors)
        elif error_type == "incorrect_use_of_exception_handling":
            return logic_bugs.incorrect_use_of_exception_handling(script,self.errors)
        elif error_type == "incorrect_use_of_builtin_function":
            return logic_bugs.incorrect_use_of_builtin_function(script,self.errors)
        else:
            raise ValueError("Invalid error type")    




class LogicBug:
    def __init__(self):
        # define lists of different types of syntax errors that can be injected
        

        self.errors = {
        "incorrect_comparison_operator": (["==", "!=", "<", "<=", ">", ">="], [r"\s*([!<=>]{1,2})\s*"]),
        "forgotten_variable_update": (["+=", "-=", "=", "/=", "%="], [r"[a-zA-Z]+\s*=\s*[a-zA-Z0-9]+"]),
        "infinite_loop": (["while", "for"], [r"while\s*[a-zA-Z0-9_\s]+:"]),
        "off_by_one_error": (["index", "slice"], [r"[[0-9]+]|[[0-9]+:[0-9]+]"]),
        
        "incorrect_function_call": (["function", "arguments"], [r"[a-zA-Z_]+\s*\([a-zA-Z0-9_\s,]*\)"]),
        "incorrect_return_value": (["return"], [r"return\s[a-zA-Z0-9_\s]+"]),
        "incorrect_boolean_operator": (["and", "or"], [r"\s(and|or)\s*"]),
        "incorrect_use_of_boolean_operators": (["if", "else"], [r"\s*(if|else)\s*"]),
        "incorrect_use_of_ternary_operator": (["if", "else"], [r"\s*(if|else)\s*"]),
        "using_wrong_type_of_loop" : (["for"], [r"for\s*[a-zA-Z0-9_\s]+\sin\s[a-zA-Z0-9_\s()]+:"]),
        "using_loop_variable_outside_loop" : (["for"], [r"for\s*[a-zA-Z0-9_\s]+\sin\s[a-zA-Z0-9_\s()]+:"]),
        "using_variable_before_assignment": ([], [r"[a-zA-Z]+\s*=\s*[a-zA-Z0-9]+"]),
        "using_wrong_variable_scope" : (["local", "global", "nonlocal"], [r"(local|global|nonlocal)\s+[a-zA-Z0-9_\s]+"]),
        "incorrect_use_of_exception_handling" : (["try", "except"], [r"(try|except)\s*[a-zA-Z0-9_\s:]+"]),
        }
        self.injector=LogicInjector(self.errors)



        self.severity_mapping = {
"easy": ["incorrect_comparison_operator", "forgotten_variable_update", "infinite_loop"],
"medium": ["off_by_one_error", "incorrect_function_call", "incorrect_return_value", "incorrect_boolean_operator", "incorrect_use_of_boolean_operators", "incorrect_use_of_ternary_operator"],
"hard": ["using_wrong_type_of_loop", "using_loop_variable_outside_loop", "using_variable_before_assignment", "using_wrong_variable_scope", "incorrect_use_of_exception_handling"]
}

    def count_injectables(self, script, error_types=None):
        error_counts = {}
        if error_types is None:
            error_types = self.errors.keys()
        for error_type, (chars, pattern) in self.errors.items():
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
        error_counts = self.count_injectables(script,error_types=error_list)
        # check if there are enough instances of the error type to inject the errors
        if sum(error_counts.values()) >= num_errors:
            modified_script = script
            errors_injected = 0
            counter = 0
            while errors_injected < num_errors and counter < 100 * num_errors:
                # choose a random error from the selected list
                random_error = random.choice(error_list)
                # print(random_error in error_list)
                # print(random_error in error_counts.keys())
                # # check if there are enough instances of the error type to inject the error
                # print(error_list)
                # print(random_error,type(random_error))
                # print(error_list[0],type(error_list[0]))
                # print(error_counts)
                # print(error_counts[error_list[0]])
                # print(error_counts[random_error])
                if error_counts[random_error] > 0:
                    modified_script = self.injector.inject(modified_script, error_type=random_error)
                    errors_injected += 1
                    error_counts[random_error] -= 1
                counter += 1
            return modified_script, errors_injected, counter
        else:
            raise ValueError("Not enough instances of the required error type in the script")



