import re

phrase = "The quick brown jumps fox over the lazy dog"
search_term = "brown fox"

# Add word boundaries to ensure exact match
pattern = r'\b' + re.escape(search_term) + r'\b'

if re.search(pattern, phrase):
    print("Exact phrase found!")
else:
    print("No exact match.")
