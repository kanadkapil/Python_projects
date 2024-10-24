import random

def guess_number(secret_number, attempts):
  print("Welcome to the Guessing Game!")

  for i in range(attempts):
    try:
      guess = int(input(f"Guess a number between 1 and 100 (attempt {i+1} of {attempts}) : "))
    except ValueError:
      print("Invalid input. Please enter a number.")
      continue

    if guess < 1 or guess > 100:
      print("Out of range. Please guess between 1 and 100.")
      continue

    if guess == secret_number:
      print(f"Congratulations! You guessed the number in {i+1} attempts.")
      break
    elif guess < secret_number:
      print("Too low. Try again!")
    else:
      print("Too high. Try again!")

  else:
    print(f"Sorry, you ran out of attempts. The secret number was {secret_number}.")

if __name__ == "__main__":
  secret_number = random.randint(1, 100)
  attempts = 5
  guess_number(secret_number, attempts)
