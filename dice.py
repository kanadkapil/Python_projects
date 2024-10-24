import random

def roll_dice():
# limit 1-6
  return random.randint(1, 6)

# if it's the first roll
first_roll = True

while True:
  if first_roll:
    choice = input("Wanna roll? (y/n): ").lower()
    first_roll = False  # flag false for subsequent rolls
  else:
    choice = input("Roll again? (y/n): ").lower()

  if choice == 'y':
    result = roll_dice()
    print(f"You rolled a {result}")
  else:
    break  # exit the loop 

print("Thanks for playing!")
