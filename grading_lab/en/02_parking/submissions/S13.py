# Compute the charge for the parking duration.
minutes = int(input())
hours = 0
while minutes > 0:
    if minutes >= 60:
        minutes -= 60
    hours += 1
fee = 30 * min(hours, 2) + 20 * min(max(hours - 2, 0), 3)
fee += 10 * max(hours - 5, 0)
print(min(fee, 160))
