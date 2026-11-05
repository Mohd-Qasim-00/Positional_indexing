
from pathlib import Path

from src.storage import load_vocabulary
from src.search import search_query

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = BASE_DIR / "output"


def main():

    vocabulary = load_vocabulary(OUTPUT_FOLDER)

    print("\n===== HINDI POSITIONAL SEARCH =====")
    print('Single word: भारत')
    print('Phrase: "भारत सरकार"')
    print('NEAR query: भारत NEAR/5 सरकार')
    print('Type exit to stop.\n')

    while True:

        query = input("Enter your query: ").strip()

        if query.lower() == "exit":
            print("Search stopped.")
            break

        if not query:
            continue

        result = search_query(
            query,
            vocabulary,
            OUTPUT_FOLDER
        )

        if result:

            print("\nMatching Documents:", len(result))

            for doc_id, positions in result.items():
                print(f"{doc_id} -> {positions}")

        else:
            print("\nNo matching documents found.")

        print("-" * 50)


if __name__ == "__main__":
    main()
