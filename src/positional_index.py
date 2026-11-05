from collections import defaultdict
from pathlib import Path

from src.preprocess import preprocess_document


def build_positional_index(documents_folder):

    index = defaultdict(lambda: {
        "cf": 0,
        "df": 0,
        "postings": {}
    })

    document_files = sorted(
        Path(documents_folder).glob("*.txt")
    )

    if not document_files:
        raise FileNotFoundError(
            f"No .txt documents found in {documents_folder}"
        )

    for file_path in document_files:

        doc_id = file_path.stem

        tokens = preprocess_document(file_path)

        for word, position in tokens:

            index[word]["cf"] += 1

            if doc_id not in index[word]["postings"]:
                index[word]["postings"][doc_id] = []

            index[word]["postings"][doc_id].append(position)

        # DF = number of documents containing the term
        for word in set(word for word, position in tokens):
            index[word]["df"] += 1

        print(f"Indexed: {doc_id}")

    return dict(index), len(document_files)