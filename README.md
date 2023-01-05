# OpenBugger
 Code to create bugged python scripts for OpenAssistant Training, maintained by https://twitter.com/Cyndesama


OpenBugger
OpenBugger is a tool for injecting various types of bugs into Python scripts in order to test the robustness of your code and practice debugging skills. It comes with a library of bug injection methods for different severity levels and error types, such as syntax errors, logic errors, and runtime errors.

Installation
To install OpenBugger, use pip:

Clone repo
```
python3 -m pip install --editable filepath_to/OpenBugger
```
Usage
To use OpenBugger, import the LogicInjector and LogicBug classes from the openbugger module and use them to create an injector and a bug, respectively. Then, call the inject() method of the injector and pass it the bug and the script as arguments. The injector will return the modified script with the injected bug.

```
from openbugger import LogicInjector, LogicBug

# Create an injector with a random severity level
injector = LogicInjector()

# Create a bug with a random error type
bug = LogicBug()

# Inject the bug into the script
modified_script = injector.inject(bug, "import random\n\nx = random.randint(0, 10)\nprint(x)")

# Print the modified script
print(modified_script)
```
You can also specify the severity level and error type manually when creating the injector and bug:
```
from openbugger import LogicInjector, LogicBug

# Create an injector with a medium severity level
injector = LogicInjector(severity="medium")

# Create a bug with a "forgotten_variable_update" error type
bug = LogicBug(error_type="forgotten_variable_update")

# Inject the bug into the script
modified_script = injector.inject(bug, "import random\n\nx = random.randint(0, 10)\nprint(x)")

# Print the modified script
print(modified_script)
```
You can also use the inject_random() method of the injector to inject a random bug into the script:

```
from openbugger import LogicInjector

# Create an injector with a random severity level
injector = LogicInjector()

# Inject a random bug into the script
modified_script = injector.inject_random("import random\n\nx = random.randint(0, 10)\nprint(x)")

# Print the modified script
print(modified_script)
```

# Done:
Syntax errors: These are mistakes in the structure of the code that prevent it from being parsed by the interpreter. Examples include missing parentheses, incorrect indentation, and mismatched quotation marks.

Logic errors: These are mistakes in the code that do not prevent it from being parsed, but cause it to behave in unintended ways. For example, using the wrong comparison operator (e.g., == instead of <) or forgetting to update a variable.
# ToDo:
Runtime errors: These are errors that occur when the code is executing, such as division by zero or trying to access an index that is out of bounds of a list.

Type errors: These are errors that occur when a value has the wrong type for a certain operation. For example, trying to concatenate a string and an integer will cause a type error.

Name errors: These are errors that occur when a name (e.g., a variable or function) is not defined in the current scope.

Import errors: These are errors that occur when a module cannot be imported due to a typo in the module name or a missing module.

Indentation errors: These are errors that occur when the indentation of the code is not consistent, which can cause issues with the structure of the code.
# FunToDo:
Use open-ai embeddings to train linear probes to detect bugs at pontentially lower cost instead of asking gpt3.5 like commonly available tools.
# Contributing
We welcome contributions to OpenBugger! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.






