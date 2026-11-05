
import re
import unicodedata

def tokenize(text):
    text = unicodedata.normalize("NFC", text)

    # Extract only Devanagari words
    tokens = re.findall(r'[\u0900-\u097F]+', text)

    result = []

    for position, token in enumerate(tokens, start=1):
        if any(
            unicodedata.category(ch).startswith("L")
            for ch in token
        ):
            result.append((token, position))

    return result


def preprocess_document(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return tokenize(text)
