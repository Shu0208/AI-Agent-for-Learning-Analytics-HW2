# Compute the charge for the parking duration.
minutes = int(input())
hours = (minutes + 59) // 60
fee = 0
for hour in range(1, hours + 1):
    if hour <= 2:
        fee += 30
    elif hour <= 5:
        fee += 20
    else:
        fee += 10
print(min(fee, 160))
