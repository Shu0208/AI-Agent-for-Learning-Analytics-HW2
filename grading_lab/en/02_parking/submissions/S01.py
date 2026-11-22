# Compute the charge for the parking duration.
minutes = int(input())
hours = (minutes + 59) // 60
first = min(hours, 2) * 30
middle = min(max(hours - 2, 0), 3) * 20
last = max(hours - 5, 0) * 10
print(min(first + middle + last, 160))
