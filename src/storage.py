import json
from pathlib import Path


def save_index(index, output_folder):

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    vocabulary = {}

    postings_path = output_path / "postings.jsonl"
    vocabulary_path = output_path / "vocabulary.json"

    with open(postings_path, "wb") as postings_file:

        for term in sorted(index.keys()):

            data = index[term]

            posting_data = {
                "term": term,
                "postings": data["postings"]
            }

            # Current byte position in the postings file
            offset = postings_file.tell()

            line = (
                json.dumps(
                    posting_data,
                    ensure_ascii=False
                ) + "\n"
            ).encode("utf-8")

            postings_file.write(line)

            vocabulary[term] = {
                "cf": data["cf"],
                "df": data["df"],
                "offset": offset
            }

    with open(vocabulary_path, "w", encoding="utf-8") as file:
        json.dump(
            vocabulary,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Vocabulary saved:", vocabulary_path)
    print("Postings saved:", postings_path)


def load_vocabulary(output_folder):

    vocabulary_path = Path(output_folder) / "vocabulary.json"

    with open(vocabulary_path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_posting(term, vocabulary, output_folder):

    if term not in vocabulary:
        return None

    postings_path = Path(output_folder) / "postings.jsonl"

    offset = vocabulary[term]["offset"]

    with open(postings_path, "rb") as file:

        file.seek(offset)
        line = file.readline()

    data = json.loads(line.decode("utf-8"))

    return data["postings"]