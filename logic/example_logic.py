import inspect
import random

from logic.logic_injector import LogicBug

# Simple example script

def simple_script():
    # Choose two random integers
    num1 = random.randint(0, 10)
    num2 = random.randint(0, 10)

    # Compare the two numbers and print a message based on their relation
    if num1 > num2:
        print("num1 is greater than num2")
    elif num1 < num2:
        print("num1 is less than num2")
    else:
        print("num1 is equal to num2")

# Medium example script
def medium_script():
    # Choose a random integer and assign it to a variable
    num = random.randint(0, 10)

    # Use a loop to print all numbers from 0 to the chosen integer
    for i in range(num):
        print(i)

# Hard example script
def hard_script():
    # Choose a random integer and assign it to a variable
    num = random.randint(0, 10)

    # Use a loop to print the square of all numbers from 0 to the chosen integer
    for i in range(num):
        print(i**2)

# create an instance of the LogicBug class
logic_bug = LogicBug()

# get the source code of the simple_script function as a string
simple_script_str = inspect.getsource(simple_script)
print("Simple",simple_script_str)
# inject a logic error into the simple_script function
modified_simple_script, error, counter = logic_bug.inject(simple_script_str, "easy",num_errors=3)
print("Modified version Simple",error,counter)
# print the modified simple_script function
print(modified_simple_script)
print("are they the same?",simple_script_str == modified_simple_script)

# get the source code of the medium_script function as a string
medium_script_str = inspect.getsource(medium_script)
print("Medium",medium_script_str)
# inject a logic error into the medium_script function
modified_medium_script, error, counter = logic_bug.inject(medium_script_str,"medium",num_errors=3)

# print the modified medium_script function
print("Modified version Medium",error,counter)
print(modified_medium_script)
print("are they the same?",medium_script_str == modified_medium_script)
# get the source code of the hard_script function as a string
hard_script_str = inspect.getsource(hard_script)
print("Hard",hard_script_str)
# inject a logic error into the hard_script function
modified_hard_script, error, counter = logic_bug.inject(hard_script_str,"hard",num_errors=1)
print("Modified version Hard",error,counter)
# print the modified hard_script function
print(modified_hard_script)
print("are they the same?",hard_script_str == modified_hard_script)
