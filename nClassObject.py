class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def intro(self):
        print(f"Hello, my name is {self.name} and I'm {self.age} years old.")

n=input ("Enter your name:")
a=int(input("Enter your age:"))
p=Person(n,a)
p.intro()