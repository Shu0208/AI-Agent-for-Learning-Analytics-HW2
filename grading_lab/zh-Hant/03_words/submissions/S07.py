# 整理文字並統計單字。
import re
import sys

counts = {}
for word in re.findall("[A-Za-z]+", sys.stdin.read()):
    key = word.lower()
    counts[key] = counts.get(key, 0) + 1
if not counts:
    print("NONE 0")
else:
    highest = max(counts.values())
    tied = [word for word, count in counts.items() if count == highest]
    print(min(tied), highest)
