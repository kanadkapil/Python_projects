class Student:
    def __init__ (self, name, roll):
        self.name = name
        self.roll = roll
    
    def display(self):
        print(f"Name: {self.name}  Roll: {self.roll}")

nameInput= str(input("Enter Name: "))
rollInput=int(input('Enter Roll Number: '))
    
SIn = Student(nameInput, rollInput)
SIn.display()
        
