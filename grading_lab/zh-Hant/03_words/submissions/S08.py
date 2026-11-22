# 整理文字並統計單字。
import re
import sys
from collections import Counter

words = re.findall(r"[a-z]+", sys.stdin.read().lower())
counts = Counter(set(words))
if counts:
    best = min(counts, key=lambda word: (-counts[word], word))
    print(best, counts[best])
else:
    print("NONE 0")
