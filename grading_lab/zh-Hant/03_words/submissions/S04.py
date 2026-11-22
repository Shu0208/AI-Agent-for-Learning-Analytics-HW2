# 整理文字並統計單字。
import re
import sys
from collections import Counter

words = re.findall(r"[A-Za-z]+", sys.stdin.read())
counts = Counter(words)
if counts:
    best = min(counts, key=lambda word: (-counts[word], word))
    print(best, counts[best])
else:
    print("NONE 0")
