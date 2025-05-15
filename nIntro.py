# -------------------------------------
# Basic Print Statement
# -------------------------------------
print("Fuck World")  # Consider using a more appropriate message in professional code

# -------------------------------------
# Variable Declaration and Printing
# -------------------------------------
name = "Alice"
age = 2
height = 1.5
isStudent = True

print(name)
print(age)
print(height)
print(isStudent)

# -------------------------------------
# Data Types Check
# -------------------------------------
print(type(name))
print(type(age))
print(type(height))
print(type(isStudent))

# -------------------------------------
# Basic Arithmetic Operations
# -------------------------------------
a = 3
b = 2

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a % b)
print(a ** b)
print(a // b)

# -------------------------------------
# Conditional Statements
# -------------------------------------
age = 17

if age >= 18:
    print("You are old enough to drive")
else:
    print("You are not old enough to drive")

# -------------------------------------
# Loop: Print Numbers from 1 to 10
# -------------------------------------
for i in range(1, 11):
    print(i)

# -------------------------------------
# Loop: Print Numbers from 1 to 10 with Step 3
# -------------------------------------
for i in range(1, 11, 3): 
    print(i)

# -------------------------------------
# Function Definition and Call
# -------------------------------------
def greet(name):
    print("Hello " + name)

greet("Kap")

# -------------------------------------
# Working with Lists
# -------------------------------------
fruits = ["apple", "banana", "cherry"]
print(fruits[1])
fruits.append("orange")
print(fruits)

# -------------------------------------
# List Indexing, Slicing, and Modification
# -------------------------------------
numbers = [1, 2, 3, 4, 5]
print(numbers[2])
print(numbers[2:5])
numbers[2] = 10
print(numbers)
print(len(numbers))
numbers.remove(10)
numbers.append(6)
print(numbers)

# -------------------------------------
# Loop Through a List
# -------------------------------------
for num in numbers:
    print(num)

# -------------------------------------
# Working with Dictionaries
# -------------------------------------
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}
print("The age is ", person["age"], ", the name is ", person["name"])  

# -------------------------------------
# Dictionary Update and Access
# -------------------------------------
person = {
    "name": "Alice",
    "age": 25,
    "is_student": True
}

print(person["name"])         # Alice
person["age"] = 26            # Update value
person["city"] = "New York"   # Add new key

print(person)

# -------------------------------------
# Function with Return Value
# -------------------------------------
def add(a, b):
    return a + b

sum = add(1, 2)
print(sum)

# -------------------------------------
# User Input and Output
# -------------------------------------
name = input("What is your name? ")
print("Hello, " + name + "!")

age = input("How old are you? ")
print("You are " + age + " years old.")

age = int(input("Enter your age: "))
print("Next year, you'll be", age + 1)

# -------------------------------------
# Error Handling with try-except
# -------------------------------------
try:
    num = int(input("Enter a number: "))
    print("You entered:", num)
except ValueError:
    print("That was not a valid number!")
