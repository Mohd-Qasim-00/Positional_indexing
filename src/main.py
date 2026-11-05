from pathlib import Path

from src.preprocess import preprocess_document
from src.positional_index import build_positional_index
from src.storage import save_index, load_vocabulary
from src.search import search_query


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_FOLDER = BASE_DIR / "dataset" / "documents"
OUTPUT_FOLDER = BASE_DIR / "output"


def write_test_results(vocabulary, output_folder):

    # Get terms ordered by collection frequency
    sorted_terms = sorted(
        vocabulary,
        key=lambda term: vocabulary[term]["cf"],
        reverse=True
    )

    if not sorted_terms:
        raise ValueError("Vocabulary is empty.")

    # Read first document to create valid phrase and NEAR examples
    document_files = sorted(DOCUMENTS_FOLDER.glob("*.txt"))

    first_tokens = preprocess_document(document_files[0])

    if len(first_tokens) < 3:
        raise ValueError(
            "First document must contain at least 3 tokens."
        )

    word1 = first_tokens[0][0]
    word2 = first_tokens[1][0]
    word3 = first_tokens[2][0]

    test_queries = [
        sorted_terms[0],
        f'"{word1} {word2}"',
        f"{word1} NEAR/5 {word3}",
        sorted_terms[min(1, len(sorted_terms) - 1)],
        f'"{word2} {word3}"'
    ]

    result_file = output_folder / "test_results.txt"

    with open(result_file, "w", encoding="utf-8") as file:

        for number, query in enumerate(test_queries, start=1):

            result = search_query(
                query,
                vocabulary,
                output_folder
            )

            file.write(f"\nTEST CASE {number}\n")
            file.write(f"Query: {query}\n")
            file.write(f"Matching documents: {len(result)}\n")

            for doc_id, positions in result.items():
                file.write(
                    f"{doc_id} -> {positions}\n"
                )

            if not result:
                file.write("No matching documents found.\n")

    print("Test results saved:", result_file)


def write_rare_terms(vocabulary, output_folder):

    # Rare terms = terms with lowest collection frequency
    rare_terms = sorted(
        vocabulary,
        key=lambda term: (
            vocabulary[term]["cf"],
            vocabulary[term]["df"],
            term
        )
    )[:10]

    result_file = output_folder / "rare_terms.txt"

    with open(result_file, "w", encoding="utf-8") as file:

        for number, term in enumerate(rare_terms, start=1):

            data = vocabulary[term]

            file.write(f"\n{number}. Term: {term}\n")
            file.write(f"CF: {data['cf']}\n")
            file.write(f"DF: {data['df']}\n")

            from src.storage import read_posting

            postings = read_posting(
                term,
                vocabulary,
                output_folder
            )

            for doc_id, positions in postings.items():
                file.write(
                    f"{doc_id} -> {positions}\n"
                )

    print("Rare terms saved:", result_file)


def write_statistics(index, total_documents, output_folder):

    total_tokens = sum(
        data["cf"] for data in index.values()
    )

    stats_file = output_folder / "index_stats.txt"

    with open(stats_file, "w", encoding="utf-8") as file:

        file.write("POSITIONAL INDEX STATISTICS\n")
        file.write("============================\n")
        file.write(f"Total documents: {total_documents}\n")
        file.write(f"Vocabulary size: {len(index)}\n")
        file.write(f"Total tokens: {total_tokens}\n")

    print("Statistics saved:", stats_file)


def main():

    print("\n===== HINDI POSITIONAL INDEXER =====\n")

    if not DOCUMENTS_FOLDER.exists():
        raise FileNotFoundError(
            f"Documents folder not found: {DOCUMENTS_FOLDER}"
        )

    # Step 1: Build positional index
    print("Step 1: Building positional index...")

    index, total_documents = build_positional_index(
        DOCUMENTS_FOLDER
    )

    # Step 2: Save vocabulary and postings
    print("\nStep 2: Saving index to disk...")

    save_index(index, OUTPUT_FOLDER)

    # Step 3: Load vocabulary into main memory
    print("\nStep 3: Loading vocabulary...")

    vocabulary = load_vocabulary(OUTPUT_FOLDER)

    # Step 4: Generate test cases
    print("\nStep 4: Running five test cases...")

    write_test_results(vocabulary, OUTPUT_FOLDER)

    # Step 5: Generate rare terms
    print("\nStep 5: Generating ten rare terms...")

    write_rare_terms(vocabulary, OUTPUT_FOLDER)

    # Step 6: Write statistics
    write_statistics(
        index,
        total_documents,
        OUTPUT_FOLDER
    )

    print("\n===== PROJECT COMPLETED =====")
    print("Total documents:", total_documents)
    print("Vocabulary size:", len(vocabulary))
    print("Output folder:", OUTPUT_FOLDER)


if __name__ == "__main__":
    main()