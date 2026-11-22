# Process the text and count the words.
import sys

letters = []
for ch in sys.stdin.read().lower():
    letters.append(ch if "a" <= ch <= "z" else " ")
words = "".join(letters).split()
frequencies = {}
for word in words:
    frequencies[word] = frequencies.get(word, 0) + 1
best = "NONE"
highest = 0
for word in sorted(frequencies):
    if frequencies[word] > highest:
        best, highest = word, frequencies[word]
print(best, highest)
