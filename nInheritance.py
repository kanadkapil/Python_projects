class Person:
    def __init__(self, name, age):
        self.name = name
        
    def greet(self):
        print(f"Hello, my name is {self.name} ")

class Student(Person):
    def __init__(self, name, roll):
        super().__init__(name)
        self.roll= roll
        
    def display(self):
        print(f"Name: {self.name}  Roll: {self.roll}")
        
s= Student("Rahul", 101)
s.greet()
s.display()
