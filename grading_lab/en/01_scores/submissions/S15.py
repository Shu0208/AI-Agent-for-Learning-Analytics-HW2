# Read the scores and produce the summary.
import sys
from statistics import mean

def summarize(values):
    if not values:
        return 0, 0.0, 0
    return len(values), mean(values), len([n for n in values if n >= 60])

scores = list(map(int, sys.stdin.read().split()))
count, average, passed = summarize(scores)
print(f"{count} {average:.2f} {passed}")
