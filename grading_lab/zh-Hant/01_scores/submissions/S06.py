# 讀取成績，再整理統計結果。
import sys

scores = [int(item) for item in sys.stdin.readline().split()]
count = len(scores)
mean = sum(scores) / count if count else 0
passing = sum(score >= 60 for score in scores)
print(f"{count} {mean:.2f} {passing}")
