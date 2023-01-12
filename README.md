# OpenBugger

Code to create bugged python scripts for OpenAssistant Training, maintained by [Cyndesama](https://twitter.com/Cyndesama)

OpenBugger

OpenBugger is a tool for injecting various types of bugs into Python scripts in order to test the robustness of your code and practice debugging skills. It comes with a library of bug injection methods for different severity levels and error types, such as syntax errors, logic errors, and runtime errors.

## Installation

To install OpenBugger, use pip:

Clone repo

```python
python3 -m pip install --editable filepath_to/OpenBugger
```

## Usage

To use OpenBugger, import the SintaxBug or LogicBug classes from the openbugger module and use them to inject a bug with a call to the inject(). The injector will return the modified script with the injected bug.

```python
from syntax.syntax_injector import SyntaxInjector, SyntaxBug

syntax_bug = SyntaxBug()



# Simple script
simple_script = """
def greet(name):
    print("Hello, " + name)

greet("Bob")
"""

print(simple_script)
```

The simple script can be modified using the "easy" injection method because it only contains simple syntax and does not have any nested code blocks.
This means that there are fewer characters (e.g. quotes, brackets, braces, parenthesis) that could be the target of syntax errors,
 and the "easy" injection method, which only injects errors that involve replacing or removing a single character, is sufficient to modify the script.

```python
# Inject easy syntax errors into the simple script

modified_simple_script, errors, counter = syntax_bug.inject(simple_script, "easy", 1)
print("Modified version Easy",errors,counter)
print(modified_simple_script)
```

Or for higher severity and logic error by directly transforming a Python class into text

```python
import inspect
import random
from logic.logic_injector import LogicBug


# Medium example script
def medium_script():
    # Choose a random integer and assign it to a variable
    num = random.randint(0, 10)

    # Use a loop to print all numbers from 0 to the chosen integer
    for i in range(num):
        print(i)

# create an instance of the LogicBug class
logic_bug = LogicBug()
# get the source code of the medium_script function as a string
medium_script_str = inspect.getsource(medium_script)
print("Medium",medium_script_str)
# inject a logic error into the medium_script function
modified_medium_script, error, counter = logic_bug.inject(medium_script_str,"medium",num_errors=3)
```

For more examples see syntax/example_syntax.py and logic/example_logic.py

## Done

Syntax errors: These are mistakes in the structure of the code that prevent it from being parsed by the interpreter. Examples include missing parentheses, incorrect indentation, and mismatched quotation marks.

Logic errors: These are mistakes in the code that do not prevent it from being parsed, but cause it to behave in unintended ways. For example, using the wrong comparison operator (e.g., == instead of <) or forgetting to update a variable.

## ToDo

Runtime errors: These are errors that occur when the code is executing, such as division by zero or trying to access an index that is out of bounds of a list.

Type errors: These are errors that occur when a value has the wrong type for a certain operation. For example, trying to concatenate a string and an integer will cause a type error.

Name errors: These are errors that occur when a name (e.g., a variable or function) is not defined in the current scope.

Import errors: These are errors that occur when a module cannot be imported due to a typo in the module name or a missing module.

Indentation errors: These are errors that occur when the indentation of the code is not consistent, which can cause issues with the structure of the code.

## FunToDo

Use open-ai embeddings to train linear probes to detect bugs at potentially lower cost instead of asking gpt3.5 like commonly available tools.

## Contributing

We welcome contributions to OpenBugger! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request. see [CONTRIBUTING](CONTRIBUTING.md) for more details.

OpenBugger is licensed under the Apache 2.0

## License

Apache License 2.0
A permissive license whose main conditions require preservation of copyright and license notices. Contributors provide an express grant of patent rights. Licensed works, modifications, and larger works may be distributed under different terms and without source code.
