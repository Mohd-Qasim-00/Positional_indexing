# Positional Index Search Engine

## Overview

This project is a small information-retrieval search engine written in Python. It reads plain-text documents from `corpus/`, builds a positional inverted index, saves the index as `positional_index.json`, and uses that index to find words, exact phrases, and pairs of words within a specified distance.

The project currently contains 100 corpus files (`doc1.txt` through `doc100.txt`). Each file is treated as one document. The engine reports matching document IDs and token positions; it does not rank results by relevance.

## Dataset: Reuters-21578

Reuters-21578 is a collection of 21,578 Reuters newswire articles commonly used in information-retrieval and text-classification exercises. The project includes 100 text files (`corpus/doc1.txt` through `corpus/doc100.txt`), not all 21,578 articles. `reuters21578/extract.py` shows how these local files are produced: it reads `reut2-000.sgm`, takes the first 100 `<REUTERS>` records in file order, and writes each record's title and body as `doc1.txt` through `doc100.txt`. The local names are not Reuters article IDs. The search scripts do not load category labels or other Reuters metadata; they index the extracted text only.

## Methodology

The search engine uses the following processing steps:

1. **Read documents:** `build_index.py` scans the `corpus/` directory and reads each `.txt` file as one document.
2. **Normalize and tokenize:** It lowercases the text and extracts ASCII alphanumeric tokens with the regular expression `\b[a-z0-9]+\b`. Numeric and mixed letter-number tokens are retained.
3. **Record positions:** It numbers tokens from 1 within each document and records every occurrence of each term.
4. **Build the positional index:** It groups the recorded positions by term and document, then saves the result to `positional_index.json`.
5. **Load the index:** `query.py` reads the saved JSON index into memory when it starts.
6. **Process a query:** The program identifies a single-word, quoted-phrase, or `NEAR/n` proximity query and searches the index. Phrase matches require consecutive positions; proximity matches allow the terms in either order within the specified distance.
7. **Display results:** It prints matching document IDs and positions. It does not calculate relevance scores or rank documents.

## Files

- `corpus/`: Source documents. The index builder processes files ending in `.txt`.
- `build_index.py`: Reads and tokenizes the corpus, constructs the positional index, and writes `positional_index.json`.
- `positional_index.json`: Generated index. Each term maps to documents and the positions where that term occurs.
- `query.py`: Loads the saved index, detects the query form, searches it, and prints results in an interactive command-line loop.
- `reuters21578/extract.py`: Optional extractor for the first 100 records in `reuters21578/reut2-000.sgm`. It requires Beautiful Soup (`beautifulsoup4`) and writes to `reuters21578/corpus/` when run from the `reuters21578/` directory.
- `reuters21578/`: Contains the source SGML collection and its accompanying Reuters-21578 files. The search engine does not read these files directly.


## How It Works

### 1. Tokenization

Both search scripts lowercase text and use the pattern `\b[a-z0-9]+\b`, so digit-only and mixed alphanumeric terms are indexed and searchable. For example, `Cocoa-market 2025` becomes `cocoa`, `market`, `2025`; `can't` becomes `can`, `t`; and `abc123` remains one token. Punctuation such as hyphens and periods separates tokens. The pattern is limited to ASCII letters and digits, so non-English letters are not indexed. There is no stemming or stop-word removal.

### 2. Building the index

Run `build_index.py` from the project directory. It visits `.txt` files directly inside `corpus/` (not subdirectories), tokenizes their contents, and assigns each token a one-based position within its document. The saved structure is conceptually:

```json
{
  "cocoa": {
    "doc1": [2, 12, 91, 116, 172, 206, 530]
  }
}
```

This says that `cocoa` appears in `doc1` at the listed token positions. A term may appear in many documents; each document has its own list of positions.

### 3. Running searches

Run `query.py` from the project directory. It loads `positional_index.json` once, then accepts queries until you type `exit`.

Use one of these query types:

1. **Search for one word:** Enter a word to find documents containing it and see all its positions. Example: `company`.
2. **Search for an exact phrase:** Put two or more consecutive words inside quotation marks. Example: `"stock market"`.
3. **Search by proximity:** Enter two words with `NEAR/n` between them. The words may appear in either order, and their positions must be no farther apart than `n`. Example: `company NEAR/5 market`.

`NEAR/5` uses an inclusive distance: positions 10 and 15 match. Phrase matching is stricter: every next word must be exactly one position after the previous word. Queries that are not one word, a quoted phrase, or the supported `word NEAR/n word` form are not searched.

## Setup and Use

Python 3 is required. Building the index and running searches use only Python's standard library. The optional Reuters extractor additionally requires Beautiful Soup 4.

Open a terminal in the project directory and build or refresh the index:

```powershell
python build_index.py
```

Then start the search program:

```powershell
python query.py
```

The checked-in `corpus/` folder is ready to index. If you need to regenerate those local text files from the SGML source, install the extractor dependency, run the extractor from its own directory, then copy its output into the project-level corpus:

```powershell
python -m pip install beautifulsoup4
Push-Location .\reuters21578
python .\extract.py
Pop-Location
Copy-Item .\reuters21578\corpus\*.txt .\corpus\
```

The extractor writes only the first 100 records from `reut2-000.sgm`; it does not process all 22 SGML files in the Reuters collection.

Example session:

```text
Search: cocoa
Search: "stock market"
Search: company NEAR/5 market
Search: exit
```

Build the index again whenever documents are added, removed, or changed. Both scripts use paths relative to the current working directory, so run them from the project directory. `query.py` requires `positional_index.json` to exist; run the build command first if it is missing or out of date.

## Complexity and Resource Use

Let:

- `F` be the number of input files.
- `T` be the total number of tokens across those files.
- `P` be the total number of indexed token occurrences. In this implementation, `P = T`.
- `U` be the number of distinct terms.
- `I` be the size of the serialized index in bytes.
- `f(t, d)` be the number of occurrences of term `t` in document `d`.

### Index construction

Reading and tokenizing the corpus takes `O(T)` time. The files are sorted by name before processing, which adds `O(F log F)` time. Adding each occurrence to the in-memory index takes constant-time average dictionary/list operations, so the overall expected time is `O(T + F log F)`. The index requires `O(P + U + D)` space, where `D` is the number of documents represented in the index; the position lists account for most of the storage.

### Loading and single-word search

Loading the JSON index takes `O(I)` time and `O(I)`-scale memory. The complete index is loaded into memory when `query.py` starts.

A single-word lookup has average `O(1)` dictionary lookup time, then iterates over the matching documents and positions to print them. If the word has `D_w` matching documents and `P_w` occurrences, the full search and output work is `O(D_w + P_w)`. Printing can be a substantial part of the time for very frequent words.

### Phrase search

The program first intersects the document sets for all phrase terms. That work depends on how many documents contain each term. For each common document, it then checks each occurrence of the first term against the other terms' position lists. Those lists are Python lists, so `position in list` is a linear scan, not a constant-time lookup.

For a phrase of `q` terms, the positional-check work is bounded by approximately:

```text
sum over common documents d of
f(first_term, d) * sum of f(each later term, d)
```

This is a worst-case style bound; unsuccessful checks may stop early. The phrase search can therefore become expensive when the first word and later words occur many times in the same documents.

### Proximity search

For each document containing both terms, the program compares every occurrence of the first word with every occurrence of the second word. Its time is:

```text
sum over common documents d of
f(word1, d) * f(word2, d)
```

The results list also uses space proportional to the number of matching pairs that are printed. Frequent terms can produce many comparisons and a large output.

## Latency and Throughput

**Latency** is the time from submitting one query until its results are printed. For this program, startup includes reading and parsing the entire JSON index. After startup, a single-word query is usually driven by the number of matching occurrences, while phrase and proximity latency also depends on how often the query terms occur together in each document. Console output and especially large result sets add to latency.

**Throughput** is the number of queries completed per unit of time, such as queries per second. This project does not include a benchmark, so no measured throughput or latency figure is claimed. Results would depend on the machine, index size, query terms, result volume, and whether startup time is included. The program handles one query at a time in one interactive process; it is not a concurrent search service.

To measure it fairly, time index loading separately from repeated searches, use a fixed set of representative word, phrase, and proximity queries, and report the corpus/index size and hardware. Avoid comparing timings where one run prints substantially more results than another.

## Current Scope and Limitations

- Exact token matching only; there is no ranking, relevance score, stemming, wildcard, or fuzzy search.
- Tokens are ASCII letters and digits; punctuation generally separates tokens, while non-English letters are excluded.
- Phrase queries require consecutive tokens and at least two words.
- Proximity uses absolute token distance and permits either order.
- The index and corpus paths are relative to the current working directory.
- `reuters21578/extract.py` also uses paths relative to the current working directory; run it from `reuters21578/`.
- The full index is held in memory, and the command-line loop processes queries serially.
- The index is a generated snapshot. Changes to corpus files are not reflected until `build_index.py` is run again.
