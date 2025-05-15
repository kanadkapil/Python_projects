# Empty list
empty = []

# List with values
numbers = [1, 2, 3]

# Mixed data types
mixed = [1, "text", 3.14]

# Nested lists
nested = [1, [2, 3], 4]


my_list = [10, 20, 30, 40]

# Indexing (0-based)
print(my_list[1])    # 20

# Negative indexing
print(my_list[-1])   # 40

# Slicing
print(my_list[1:3])  # [20, 30]


my_list = [1, 2, 3]

# Change value
my_list[0] = 100

# Add item
my_list.append(4)         # [100, 2, 3, 4]
my_list.insert(1, 200)    # [100, 200, 2, 3, 4]

# Extend list
my_list.extend([5, 6])    # [100, 200, 2, 3, 4, 5, 6]

# Remove item
my_list.remove(200)
del my_list[0]
item = my_list.pop()      # Removes last item

# Clear list
my_list.clear()
print(my_list)



a = [1, 2]
b = [3, 4]

# Concatenation
c = a + b      # [1, 2, 3, 4]

# Repetition
d = a * 2      # [1, 2, 1, 2]

# Membership
2 in a         # True
5 not in a     # True

# Length
print(len(a))         # 2



# /////////////////////

my_list = [10, 20, 30, 40]


for item in my_list:
    print(item)

# Using index
for i in range(len(my_list)):
    print(my_list[i])



list2=[3,6,9,4,5,8,1,2]
print(list2)
for i in list2:
    print(i)
list2.sort()
print(list2)
print(len(list2))
print(sum(list2))
print(min(list2))
print(max(list2))
print(sorted(list2))



a = [1, 2, 3]

# Shallow copies
b = a.copy()
c = a[:]
print(b)
print(c)    
print(b+c)

# Deep copy (for nested lists)
import copy
d = copy.deepcopy(a)
print(d)



a = [1, 2, 3]
x, y, z = a
print(x)
print(y)    
print(z)
print(a)

# basically tuple is like an array and list lis like a vector 