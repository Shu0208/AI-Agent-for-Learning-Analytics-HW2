# Read the scores and produce the summary.
import sys

scores = [int(item) for item in sys.stdin.readline().split()]
count = len(scores)
mean = sum(scores) / count if count else 0
passing = sum(score >= 60 for score in scores)
print(f"{count} {mean:.2f} {passing}")
