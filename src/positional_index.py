from collections import defaultdict
from pathlib import Path

from src.preprocess import preprocess_document


def iter_document_postings(documents_folder):
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
        document_postings = defaultdict(list)

        for word, position in tokens:
            document_postings[word].append(position)

        print(f"Indexed: {doc_id}")
        yield doc_id, document_postings