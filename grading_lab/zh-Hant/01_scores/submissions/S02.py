# 讀取成績，再整理統計結果。
import sys

total = passed = count = 0
for token in sys.stdin.read().split():
    score = int(token)
    count += 1
    total += score
    if score >= 60:
        passed += 1
average = total / count if count else 0
print(count, format(average, ".2f"), passed)
