# Compute the charge for the parking duration.
minutes = int(input())
hours = (minutes + 59) // 60
rate = 30 if hours <= 2 else (20 if hours <= 5 else 10)
print(min(hours * rate, 160))
