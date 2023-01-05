from syntax.syntax_injector import SyntaxInjector, SyntaxBug

syntax_bug = SyntaxBug()



# Simple script
simple_script = """
def greet(name):
    print("Hello, " + name)

greet("Bob")
"""

# The simple script can be modified using the "easy" injection method because it only contains simple syntax and does not have any nested code blocks. This means that there are fewer characters (e.g. quotes, brackets, braces, parenthesis) that could be the target of syntax errors, and the "easy" injection method, which only injects errors that involve replacing or removing a single character, is sufficient to modify the script.
print(simple_script)
# Inject easy syntax errors into the simple script

modified_simple_script, errors, counter = syntax_bug.inject(simple_script, "easy", 1)
print("Modified version Easy",errors,counter)
print(modified_simple_script)
print("are they the same?",simple_script == modified_simple_script)
# Medium script
medium_script = """
def greet(name):
    print("Hello, " + name)
    
def greet_all(names):
    for name in names:
        greet(name)
        
greet_all(["Bob", "Alice", "Eve"])
"""

# The medium script can be modified using the "medium" injection method because it contains a nested code block (the for loop in the `greet_all` function). This means that there are more characters (e.g. quotes, brackets, braces, parenthesis) that could be the target of syntax errors, and the "medium" injection method, which injects errors that involve replacing, removing, or adding a single character, is sufficient to modify the script.
print(medium_script)
# Inject medium syntax errors into the medium script
modified_medium_script, errors, counter = syntax_bug.inject(medium_script, "medium", 3)
print("Modified version Medium",errors,counter)
print(modified_medium_script)
print("are they the same?",medium_script == modified_medium_script)
# Hard script
hard_script = """
class Greeting:
    def __init__(self, greeting):
        self.greeting = greeting
        
    def greet(self, name):
        print(self.greeting + ", " + name)
        
greeting = Greeting("Hello")
greeting.greet("Bob")
"""

# The hard script can be modified using the "hard" injection method because it contains multiple nested code blocks (the `__init__` and `greet` methods in the `Greeting` class). This means that there are even more characters (e.g. quotes, brackets, braces, parenthesis) that could be the target of syntax errors, and the "hard" injection method, which injects errors that involve replacing, removing, adding, or swapping characters, is sufficient to modify the script.
print(hard_script)
# Inject hard syntax errors into the hard script
modified_hard_script, errors, counter = syntax_bug.inject(hard_script, "hard", 3)
print("Modified version Hard",errors,counter)
print(modified_hard_script)
print("are they the same?",hard_script == modified_hard_script)
