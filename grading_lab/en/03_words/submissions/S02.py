# Process the text and count the words.
import re
import sys
from collections import Counter

words = re.findall(r"[a-z]+", sys.stdin.read().lower())
counts = Counter(words)
if counts:
    best = max(counts, key=counts.get)
    print(best, counts[best])
else:
    print("NONE 0")
