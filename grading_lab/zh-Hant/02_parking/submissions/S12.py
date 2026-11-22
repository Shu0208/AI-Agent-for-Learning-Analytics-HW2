# 依停留時間計算停車費。
import math

minutes = int(input())
hours = math.ceil(minutes / 60)
if hours <= 2:
    fee = 30 * hours
elif hours <= 5:
    fee = 60 + 20 * (hours - 2)
else:
    fee = 120 + 10 * (hours - 5)
print(min(fee, 160))
