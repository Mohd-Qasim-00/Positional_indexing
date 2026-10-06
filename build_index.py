import os
import re
import json
from collections import defaultdict


CORPUS_FOLDER = "corpus"


positional_index = defaultdict(lambda: defaultdict(list))


def tokenize(text):
  
    text = text.lower()

    
    words = re.findall(r"\b[a-z0-9]+\b", text)

    return words



for filename in sorted(os.listdir(CORPUS_FOLDER)):

    if not filename.endswith(".txt"):
        continue

    doc_id = filename.replace(".txt", "")

    filepath = os.path.join(CORPUS_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()

    words = tokenize(text)

   
    for position, word in enumerate(words, start=1):
        positional_index[word][doc_id].append(position)



positional_index = {
    word: dict(documents)
    for word, documents in positional_index.items()
}



with open("positional_index.json", "w", encoding="utf-8") as file:
    json.dump(positional_index, file, indent=4)


print("Positional index created successfully!")
print("Total unique terms:", len(positional_index))