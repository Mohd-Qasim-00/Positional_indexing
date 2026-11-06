import json
from pathlib import Path


def save_index(document_postings, output_folder):

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    vocabulary = {}
    total_documents = 0

    postings_path = output_path / "postings.jsonl"
    vocabulary_path = output_path / "vocabulary.json"

    with open(postings_path, "wb") as postings_file:
        for doc_id, terms in document_postings:
            total_documents += 1

            for term, positions in terms.items():
                offset = postings_file.tell()
                posting_data = {
                    "doc_id": doc_id,
                    "positions": positions
                }
                line = (
                    json.dumps(posting_data, ensure_ascii=False) + "\n"
                ).encode("utf-8")
                postings_file.write(line)

                term_data = vocabulary.setdefault(term, {
                    "cf": 0,
                    "df": 0,
                    "offsets": []
                })
                term_data["cf"] += len(positions)
                term_data["df"] += 1
                term_data["offsets"].append(offset)

    with open(vocabulary_path, "w", encoding="utf-8") as file:
        json.dump(
            vocabulary,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Vocabulary saved:", vocabulary_path)
    print("Postings saved:", postings_path)
    return total_documents


def load_vocabulary(output_folder):

    vocabulary_path = Path(output_folder) / "vocabulary.json"

    with open(vocabulary_path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_posting(term, vocabulary, output_folder):

    if term not in vocabulary:
        return None

    postings_path = Path(output_folder) / "postings.jsonl"
    postings = {}

    with open(postings_path, "rb") as file:
        for offset in vocabulary[term]["offsets"]:
            file.seek(offset)
            data = json.loads(file.readline().decode("utf-8"))
            postings[data["doc_id"]] = data["positions"]

    return postings