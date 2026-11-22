# 依停留時間計算停車費。
minutes = int(input())
hours = minutes // 60 + 1
first = min(hours, 2) * 30
middle = min(max(hours - 2, 0), 3) * 20
last = max(hours - 5, 0) * 10
print(min(first + middle + last, 160))
