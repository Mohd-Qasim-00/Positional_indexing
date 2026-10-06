import json
import re


with open("positional_index.json", "r", encoding="utf-8") as file:
    index = json.load(file)




def tokenize(text):
   

    return re.findall(r"\b[a-z0-9]+\b", text.lower())




def single_word_query(word):

    word = word.lower()

    if word not in index:
        print(f"\n'{word}' not found in the index.")
        return

    print(f"\nResults for: {word}")
    print("-" * 50)

    for doc_id, positions in index[word].items():
        print(f"{doc_id} -> positions {positions}")




def phrase_query(words):


    for word in words:

        if word not in index:
            print(f"\n'{word}' not found in the index.")
            return

    common_docs = set(index[words[0]].keys())

    for word in words[1:]:
        common_docs &= set(index[word].keys())

    if not common_docs:
        print("\nNo phrase match found.")
        return

    phrase_matches = {}

   
    for doc_id in common_docs:

        
        first_positions = index[words[0]][doc_id]

        matches = []

        
        for start_position in first_positions:

            matched = True

            
            for i in range(1, len(words)):

                expected_position = start_position + i

                if expected_position not in index[words[i]][doc_id]:

                    matched = False
                    break

            if matched:
                matches.append(start_position)

        if matches:
            phrase_matches[doc_id] = matches

   
    if not phrase_matches:
        print("\nNo exact phrase match found.")
        return

    
    print("\nPhrase Query Results")
    print("-" * 50)

    for doc_id, positions in phrase_matches.items():

        print(
            f"{doc_id}-> {positions}"
        )




def proximity_query(word1, word2, distance):

    word1 = word1.lower()
    word2 = word2.lower()

    # Check first word/number
    if word1 not in index:

        print(f"\n'{word1}' not found in the index.")
        return

   
    if word2 not in index:

        print(f"\n'{word2}' not found in the index.")
        return

   
    common_docs = (
        set(index[word1].keys())
        &
        set(index[word2].keys())
    )

    if not common_docs:

        print("\nNo documents contain both terms.")
        return

    results = {}

    
    for doc_id in common_docs:

        positions1 = index[word1][doc_id]
        positions2 = index[word2][doc_id]

        matches = []

        
        for p1 in positions1:

            for p2 in positions2:

                if abs(p1 - p2) <= distance:

                    matches.append((p1, p2))

        if matches:

            results[doc_id] = matches

   
    if not results:

        print(
            f"\nNo documents found within NEAR/{distance}."
        )

        return

   
    print(
        f"\nProximity Query: "
        f"{word1} NEAR/{distance} {word2}"
    )

    print("-" * 50)

    for doc_id, matches in results.items():

        print(f"\n{doc_id}")

        for p1, p2 in matches:

            print(
                f"  {word1} at position {p1}, "
                f"{word2} at position {p2}"
            )




def search(query):

    query = query.strip()

    # Empty query
    if not query:

        print("Please enter a query.")
        return


    

    proximity_pattern = re.fullmatch(
        r"\s*([a-zA-Z0-9]+)\s+NEAR/(\d+)\s+([a-zA-Z0-9]+)\s*",
        query,
        re.IGNORECASE
    )

    if proximity_pattern:

        word1 = proximity_pattern.group(1).lower()

        distance = int(
            proximity_pattern.group(2)
        )

        word2 = proximity_pattern.group(3).lower()

        proximity_query(
            word1,
            word2,
            distance
        )

        return


    

    if (
        len(query) >= 2
        and query.startswith('"')
        and query.endswith('"')
    ):

        
        phrase = query[1:-1]

        
        words = tokenize(phrase)

       
        if len(words) < 2:

            print(
                "\nPlease enter at least two words "
                "inside quotes."
            )

            return

        phrase_query(words)

        return




    words = tokenize(query)

    if len(words) == 1:

        single_word_query(words[0])

        return


   

    print(
        "\nFor a phrase query, use quotation marks."
    )

    print(
        'Example: "stock market"'
    )

    

    print(
        "\nFor proximity search, use:"
    )

    print(
        "company NEAR/5 market"
    )

    print(
        "2023 NEAR/5 company"
    )



print("=" * 60)

print(
    "          POSITIONAL INDEX SEARCH ENGINE"
)

print("=" * 60)


print("""
Enter your query directly.

Examples:

  company
  2023
  "stock market"
  company NEAR/5 market
  2023 NEAR/5 company

Type 'exit' to close.
""")



while True:

    query = input("\nSearch: ")


    if query.strip().lower() == "exit":

        print("\nSearch engine closed.")

        break

    
    search(query)