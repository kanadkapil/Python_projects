import calendar

yy = 2024
mm = 12

# Adding space on top and bottom
print("\n" * 2)
# Print the month in green
print("\033[92m" + calendar.month(yy, mm) + "\033[0m")
print("\n" * 2)
