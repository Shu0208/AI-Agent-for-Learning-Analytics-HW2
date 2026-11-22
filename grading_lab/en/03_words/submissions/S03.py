# Process the text and count the words.
import re
import sys
from collections import Counter

words = sys.stdin.read().lower().split()
counts = Counter(words)
if counts:
    best = min(counts, key=lambda word: (-counts[word], word))
    print(best, counts[best])
else:
    print("NONE 0")
