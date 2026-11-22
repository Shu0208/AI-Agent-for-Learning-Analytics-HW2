# 依停留時間計算停車費。
minutes = int(input())
hours = max(1, (minutes + 59) // 60)
first = min(hours, 2) * 30
middle = min(max(hours - 2, 0), 3) * 20
last = max(hours - 5, 0) * 10
print(min(first + middle + last, 160))
