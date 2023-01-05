import random


class SyntaxInjector:
        
    def inject(script, characters,error_type):
        if error_type == "missing_quote" or error_type == "missing_bracket" or error_type == "missing_brace" or error_type == "missing_parenthesis":
            # remove a random instance of the character from the script
            return script.replace(random.choice(characters), "", 1)
        elif error_type == "typo_quote" or error_type == "typo_bracket" or error_type == "typo_brace" or error_type == "typo_parenthesis":
            # replace a random instance of one character with the other character
            char_to_replace, replacement_char = random.choices(characters,k=2)

            replacement_char = characters[0]
            return script.replace(char_to_replace, replacement_char, 1)
        elif error_type == "extra_quote" or error_type == "extra_bracket" or error_type == "extra_brace" or error_type == "extra_parenthesis":
            # insert an extra instance of one of the characters at a random position in the script
            insert_char = random.choice(characters)
            insert_index = random.randint(0, len(script)-1)
            return script[:insert_index] + insert_char + script[insert_index:]
        elif error_type == "misplaced_quote" or error_type == "misplaced_bracket" or error_type == "misplaced_brace" or error_type == "misplaced_parenthesis":
            # swap the positions of two random instances of the character in the script
            char_indices = [i for i in range(len(script)) if script[i] in characters]
            if len(char_indices) < 2:
                return script
            index1, index2 = random.sample(char_indices, 2)
            modified_list = list(script)
            modified_list[index1], modified_list[index2] = modified_list[index2], modified_list[index1]
            return "".join(modified_list)
        else:
            raise ValueError("Invalid error type")



class SyntaxBug:
    def __init__(self):
        self.injector=SyntaxInjector
        # define lists of different types of syntax errors that can be injected
        self.errors = {
            "missing_quote": ["'", '"'],
            "missing_bracket": ["[", "]"],
            "missing_brace": ["{", "}"],
            "missing_parenthesis": ["(", ")"],
            "typo_quote": ["'", '"'],
            "typo_bracket": ["[", "]"],
            "typo_brace": ["{", "}"],
            "typo_parenthesis": ["(", ")"],
            "extra_quote": ["'", '"'],
            "extra_bracket": ["[", "]"],
            "extra_brace": ["{", "}"],
            "extra_parenthesis": ["(", ")"],
            "misplaced_quote": ["'", '"'],
            "misplaced_bracket": ["[", "]"],
            "misplaced_brace": ["{", "}"],
            "misplaced_parenthesis": ["(", ")"],
        }   
        self.severity_mapping = {
    "easy": ["typo_quote", "typo_bracket", "typo_brace", "typo_parenthesis"],
    "medium": ["missing_quote", "missing_bracket", "missing_brace", "missing_parenthesis"] + ["typo_quote", "typo_bracket", "typo_brace", "typo_parenthesis"],
    "hard": ["missing_quote", "missing_bracket", "missing_brace", "missing_parenthesis"] + ["typo_quote", "typo_bracket", "typo_brace", "typo_parenthesis"] + ["extra_quote", "extra_bracket", "extra_brace", "extra_parenthesis"] + ["misplaced_quote", "misplaced_bracket", "misplaced_brace", "misplaced_parenthesis"],
}
    def inject(self, script, severity, num_errors):
        if severity not in self.severity_mapping:
            raise ValueError("Invalid severity level")
            
        error_list = self.severity_mapping[severity]
        
        # count the number of instances of each character in the script
        char_counts = {char: script.count(char) for error_type in error_list for char in self.errors[error_type][0]}
        # check if there are enough instances of the character to inject the errors
        if sum(char_counts.values()) >= num_errors:
            modified_script = script
            errors_injected = 0
            counter = 0
            while errors_injected < num_errors and counter < 100 * num_errors:
                # choose a random error from the selected list
                error_type = random.choice(error_list)
                characters= self.errors[error_type]
                
                # check if there are enough instances of the character to inject the error
                char_counts = {char: modified_script.count(char) for error_type in error_list for char in self.errors[error_type][0]}
                if sum(char_counts.values()) >= num_errors - errors_injected :
                  new_modified_script = self.injector.inject(modified_script, characters,error_type)
                  if not new_modified_script == modified_script:
                    modified_script=new_modified_script
                    errors_injected += 1
                counter += 1
            return modified_script, errors_injected , counter
        else:
            raise ValueError("Not enough instances of the required characters in the script")

