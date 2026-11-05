import re

from src.storage import read_posting


def search_word(term, vocabulary, output_folder):

    postings = read_posting(
        term, vocabulary, output_folder
    )

    if postings is None:
        return {}

    return postings


def search_phrase(phrase, vocabulary, output_folder):

    terms = phrase.split()

    if not terms:
        return {}

    result = search_word(
        terms[0], vocabulary, output_folder
    )

    for term in terms[1:]:

        next_postings = search_word(
            term, vocabulary, output_folder
        )

        new_result = {}

        for doc_id, positions in result.items():

            if doc_id not in next_postings:
                continue

            next_positions = set(next_postings[doc_id])

            matching_positions = [
                pos for pos in positions
                if pos + 1 in next_positions
            ]

            if matching_positions:
                new_result[doc_id] = matching_positions

        result = new_result

    return result


def search_near(term1, term2, distance, vocabulary, output_folder):

    postings1 = search_word(
        term1, vocabulary, output_folder
    )

    postings2 = search_word(
        term2, vocabulary, output_folder
    )

    result = {}

    for doc_id, positions1 in postings1.items():

        if doc_id not in postings2:
            continue

        positions2 = postings2[doc_id]
        matches = []

        for p1 in positions1:
            for p2 in positions2:

                # NEAR/k: at most k intervening tokens
                if 0 < abs(p1 - p2) <= distance + 1:
                    matches.append((p1, p2))

        if matches:
            result[doc_id] = matches

    return result


def search_query(query, vocabulary, output_folder):

    query = query.strip()

    # Phrase query: "भारत की"
    if query.startswith('"') and query.endswith('"'):

        phrase = query[1:-1].strip()

        return search_phrase(
            phrase, vocabulary, output_folder
        )

    # NEAR query: भारत NEAR/5 दिल्ली
    near_match = re.fullmatch(
        r'(\S+)\s+NEAR/(\d+)\s+(\S+)',
        query,
        flags=re.IGNORECASE
    )

    if near_match:

        term1 = near_match.group(1)
        distance = int(near_match.group(2))
        term2 = near_match.group(3)

        return search_near(
            term1,
            term2,
            distance,
            vocabulary,
            output_folder
        )

    # Single word query
    return search_word(
        query, vocabulary, output_folder
    )