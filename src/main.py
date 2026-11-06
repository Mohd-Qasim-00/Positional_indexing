from pathlib import Path

from src.preprocess import preprocess_document
from src.positional_index import iter_document_postings
from src.storage import save_index, load_vocabulary
from src.search import search_query
from src.storage import read_posting


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_FOLDER = BASE_DIR / "dataset" / "documents"
OUTPUT_FOLDER = BASE_DIR / "output"


def build_reference_index(document_files, terms):
    """Build expected postings directly from source documents for checking."""
    reference = {}

    for document_path in document_files:
        for term, position in preprocess_document(document_path):
            if term in terms:
                reference.setdefault(term, {}).setdefault(
                    document_path.stem, []
                ).append(position)

    return reference


def expected_phrase(terms, reference):
    if not terms:
        return {}

    result = {}
    first_term_postings = reference.get(terms[0], {})

    for doc_id, start_positions in first_term_postings.items():
        term_position_sets = [
            set(reference.get(term, {}).get(doc_id, []))
            for term in terms[1:]
        ]
        matches = [
            start for start in start_positions
            if all(
                start + offset + 1 in positions
                for offset, positions in enumerate(term_position_sets)
            )
        ]
        if matches:
            result[doc_id] = matches

    return result


def expected_near(term1, term2, distance, reference):
    result = {}
    postings1 = reference.get(term1, {})
    postings2 = reference.get(term2, {})

    for doc_id, positions1 in postings1.items():
        positions2 = postings2.get(doc_id, [])
        matches = [
            (p1, p2)
            for p1 in positions1
            for p2 in positions2
            if 0 < abs(p1 - p2) <= distance + 1
        ]
        if matches:
            result[doc_id] = matches

    return result


def write_test_results(vocabulary, output_folder):
    document_files = sorted(DOCUMENTS_FOLDER.glob("*.txt"))
    if not document_files:
        raise FileNotFoundError(f"No .txt documents found in {DOCUMENTS_FOLDER}")

    first_tokens = preprocess_document(document_files[0])
    if len(first_tokens) < 3:
        raise ValueError("The first document must contain at least 3 tokens.")

    word1, word2, word3 = [token for token, _ in first_tokens[:3]]
    rare_term = min(
        vocabulary,
        key=lambda term: (vocabulary[term]["cf"], vocabulary[term]["df"], term)
    )
    reference = build_reference_index(
        document_files, {rare_term, word1, word2, word3}
    )
    missing_term = "अप्राप्यपरीक्षणशब्द"
    while missing_term in reference:
        missing_term += "क"

    test_cases = [
        ("Single term (positive)", rare_term, reference.get(rare_term, {})),
        ("Exact phrase (positive)", f'"{word1} {word2}"', expected_phrase([word1, word2], reference)),
        ("Exact phrase (negative)", f'"{word1} {missing_term}"', {}),
        ("NEAR/1 (positive)", f"{word1} NEAR/1 {word3}", expected_near(word1, word3, 1, reference)),
        ("NEAR/1 (negative)", f"{word1} NEAR/1 {missing_term}", {}),
    ]

    result_file = output_folder / "test_results.txt"
    passed = 0
    with open(result_file, "w", encoding="utf-8") as file:
        file.write("POSITIONAL SEARCH CHECKS\n")
        file.write("Expected results are calculated independently from the source documents.\n")

        for number, (description, query, expected) in enumerate(test_cases, start=1):
            actual = search_query(query, vocabulary, output_folder)
            success = actual == expected
            passed += int(success)

            file.write(f"\nTEST CASE {number}: {description}\n")
            file.write(f"Query: {query}\n")
            file.write(f"Status: {'PASS' if success else 'FAIL'}\n")
            file.write(f"Expected matching documents: {len(expected)}\n")
            file.write(f"Actual matching documents: {len(actual)}\n")

            if not success:
                file.write(f"Expected results: {expected}\n")
                file.write(f"Actual results: {actual}\n")
            elif actual:
                for doc_id, positions in actual.items():
                    file.write(f"{doc_id} -> {positions}\n")
            else:
                file.write("No matching documents found, as expected.\n")

        file.write(f"\nSUMMARY: {passed}/{len(test_cases)} checks passed.\n")

    print(f"Search checks: {passed}/{len(test_cases)} passed")
    print("Test results saved:", result_file)
    if passed != len(test_cases):
        raise AssertionError(f"Only {passed}/{len(test_cases)} search checks passed.")


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


def write_statistics(vocabulary, total_documents, output_folder):

    total_tokens = sum(
        data["cf"] for data in vocabulary.values()
    )

    stats_file = output_folder / "index_stats.txt"

    with open(stats_file, "w", encoding="utf-8") as file:

        file.write("POSITIONAL INDEX STATISTICS\n")
        file.write("============================\n")
        file.write(f"Total documents: {total_documents}\n")
        file.write(f"Vocabulary size: {len(vocabulary)}\n")
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

    total_documents = save_index(
        iter_document_postings(DOCUMENTS_FOLDER), OUTPUT_FOLDER
    )

    # Step 2: Load vocabulary into main memory
    print("\nStep 2: Loading vocabulary...")

    vocabulary = load_vocabulary(OUTPUT_FOLDER)

    # Step 3: Generate test cases
    print("\nStep 3: Running five test cases...")

    write_test_results(vocabulary, OUTPUT_FOLDER)

    # Step 4: Generate rare terms
    print("\nStep 4: Generating ten rare terms...")

    write_rare_terms(vocabulary, OUTPUT_FOLDER)

    # Step 5: Write statistics
    write_statistics(
        vocabulary,
        total_documents,
        OUTPUT_FOLDER
    )

    print("\n===== PROJECT COMPLETED =====")
    print("Total documents:", total_documents)
    print("Vocabulary size:", len(vocabulary))
    print("Output folder:", OUTPUT_FOLDER)


if __name__ == "__main__":
    main()
