# check vowels 

# s = input("Input a letter: ")
# vowels = ["a", "e", "i", "o", "u" , "A", "E", "I", "O", "U"]

# if s in vowels:
#     print("Vowel")
# else:
#     print("Consonant")


# Write a program that counts the number of vowels in a string.

x = input("Enter a string: ")
vowels = "aeiouAEIOU"
count = 0

for i in x:
    if i in vowels:
        count += 1
print("Number of Vowels:",count)

