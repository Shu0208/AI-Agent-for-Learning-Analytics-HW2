# Read the scores and produce the summary.
import sys

scores = [int(item) for item in sys.stdin.read().split()]
count = len(scores)
mean = sum(scores) / count
passing = sum(score >= 60 for score in scores)
print(f"{count} {mean:.2f} {passing}")
