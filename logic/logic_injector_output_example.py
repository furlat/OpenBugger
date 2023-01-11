mvp_logic_output_example=[ ("""
x = 5
y = 10
if x > y:
    print("x is greater than y")
else:
    print("x is less than or equal to y")
""", """
x = 5
y = 10
if x < y:
    print("x is greater than y")
else:
    print("x is less than or equal to y")
""",  "incorrect_comparison_operator")

, ("""
counter = 0
for i in range(10):
    counter += 1
print(counter)
""", """
counter = 0
for i in range(10):
    # missing update of variable counter
print(counter)
""", "forgotten_variable_update")

, ("""
counter = 0
while counter < 10:
    print(counter)
    counter += 1
""", """
counter = 0
while True:
    print(counter)
    counter += 1
""", "infinite_loop")

, ("""
numbers = [1, 2, 3, 4, 5]
for i in range(len(numbers)):
    print(numbers[i])
""", """
numbers = [1, 2, 3, 4, 5]
for i in range(len(numbers) + 1):
    print(numbers[i])
""", "off_by_one_error")

, ("""
def add(x, y):
    return x + y
result = add(5, 10)
print(result)
""", """
def add(x, y):
    return x + y
result = add(5)
print(result)
""", "incorrect_function_call")

, ("""
def add(x, y):
    return x + y
result = add(5, 10)
print(result)
""", """
def add(x, y):
    return x - y # incorrect return value
result = add(5, 10)
print(result)
""", "incorrect_return_value")

, ("""
x = True
y = False
if x or y:
    print("At least one of x or y is true")
else:
    print("Both x and y are false")
""", """
x = True
y = False
if x and y:
    print("At least one of x or y is true")
else:
    print("Both x and y are false")
""", "incorrect_use_of_boolean_operators")

, ("""
x = 5
y = 10
result = "x is greater than y" if x > y else "x is less than or equal to y"
print(result)
""", """
x = 5
y = 10
result = "x is less than y" if x < y else "x is less than or equal to y"
print(result)
""", "incorrect_use_of_ternary_operator")


, ("""
numbers = [1, 2, 3, 4, 5]
for number in numbers:
    print(number)
""", """
numbers = [1, 2, 3, 4, 5]
i = 0
while i < len(numbers):
    print(numbers[i])
    i += 1
""", "using_wrong_type_of_loop")



, ("""
numbers = [1, 2, 3, 4, 5]
for number in numbers:
    print(number)
print("All numbers:", numbers)
""", """
numbers = [1, 2, 3, 4, 5]
for number in numbers:
    print(number)
    numbers.remove(number)
print("All numbers:", numbers)
""", "using_loop_variable_outside_loop")


, ("""
x = 5
print(x)
""", """
print(x)
x = 5
""", "using_variable_before_assignment")

, ("""
x = 5
def scope_example():
    y = x + 1
    print(y)

scope_example()
print(x)
""", """
x = 5
def scope_example():
    x = x + 1
    print(x)

scope_example()
print(x)
""", "using_wrong_variable_scope")


, ("""
try:
    print(1/0)
except ZeroDivisionError as e:
    print("Cannot divide by zero:", e)
""", """
try:
    print(1/0)
except ValueError as e:
    print("Invalid Value:", e)
""", "incorrect_use_of_exception_handling") ]

def output_list_of_tuples_to_dict(lst):
    output_dict = {}
    for example, bugged, bug_type in lst:
        output_dict[bug_type] = (example, bugged)
    return output_dict


mvp_output_dict = output_list_of_tuples_to_dict(mvp_logic_output_example)
