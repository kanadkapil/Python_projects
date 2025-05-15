fruits=["apple","banana","cherry"]  
for i in range(len(fruits)):  
    print(f"Fruit {i} is: {fruits[i]}")
    
for a in range(len(fruits)):print(fruits[a])


matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print(matrix[1][2])  # 6 (row 2, column 3)

people = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30}
]

print(people[1]["name"])  # Bob

n = [1, 2, 3, 6, 5]
print(n[1:4])
sq=[x*x for x in n]
print(sq)
even = [x for x in n if x % 2 == 0]
print(even)  
