print("Fuck World")

name = "Alice"
age =2
height = 1.5
isStudent = True

print(name)
print(age)
print(height)
print(isStudent)

print(type(name))
print(type(age))
print(type(height))
print(type(isStudent))

a= 3
b= 2

print(a+b)
print(a-b)
print(a*b)
print(a/b)

print(a%b)
print(a**b)
print(a//b)

age = 17

if age>=18:
    print("You are old enough to drive")
else:
    print("You are not old enough to drive")


for i in range(1, 11):
    print(i)

# divided by 3 
for i in range(1, 11, 3): 
    print(i)


def greet (name):
    print("Hello " + name)

greet("Kap")


# list
fruits = ["apple", "banana", "cherry"]
print(fruits[1])
fruits.append("orange")
print(fruits)



numbers =[1, 2, 3, 4, 5]
print(numbers[2])
print(numbers[2:5])
numbers[2] = 10
print(numbers)
print(len(numbers))
numbers.remove(10)
numbers.append(6)
print(numbers)

for num in numbers:
    print(num)

# dictionary
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}
print("The age is ", person["age"], ", the name is ", person["name"])  


person = {
    "name": "Alice",
    "age": 25,
    "is_student": True
}

print(person["name"])         # Alice
person["age"] = 26            # Update value
person["city"] = "New York"   # Add new key

print(person)


def add(a,b):
    return a+b
sum = add(1,2)
print(sum)

# name = input("What is your name? ")
# print("Hello, " + name + "!")

# age = input("How old are you? ")
# print("You are " + age + " years old.")
# age = int(input("Enter your age: "))
# print("Next year, you'll be", age + 1)


try:
    num = int(input("Enter a number: "))
    print("You entered:", num)
except ValueError:
    print("That was not a valid number!")
