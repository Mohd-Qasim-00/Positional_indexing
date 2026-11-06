# Hindi Positional Index

This project builds and searches a positional inverted index for Hindi text.
The included collection contains 100 UTF-8 text files of Hindi Wikipedia
articles. For each indexed term, the index records collection frequency (CF),
document frequency (DF), and every token position in each document where the
term occurs. The search program supports single-term, exact-phrase, and
`NEAR/k` queries.

## Dataset and tokenization

The supplied dataset is in `dataset/documents/`, with files named `DOC1.txt`
through `DOC100.txt`. The optional `download_dataset.py` script uses the Hindi
Wikipedia API to collect articles from selected categories and save their plain
text in that folder. It requests up to 100 articles. Downloading requires an
internet connection and the optional `requests` package.

`src/preprocess.py` normalizes input to Unicode NFC and extracts Devanagari
sequences. Other scripts are ignored. Token positions start at 1 for each
document and count the extracted Devanagari tokens. The same preprocessing
rules are used during indexing and when generating test expectations.

## Requirements

- Python 3.8 or newer.
- The included documents in `dataset/documents/` (or an internet connection
  to download documents).
- The `requests` package only when using `download_dataset.py`.

Install the optional download dependency from the project folder:

```powershell
python -m pip install requests
```

## How to run

Open a terminal in the project folder (the folder containing this README).
On Windows, change to the project folder in PowerShell, for example:

```powershell
cd "C:\path\to\S20240010149--A1-PostIndex-IR-M2026"
```

### 1. Build the index and reports

The included dataset is ready to use. Run:

```powershell
python -m src.main
```

This processes the text files, writes the vocabulary and positional postings
to `output/`, loads the vocabulary for searching, runs five search checks, and
regenerates the rare-term and index-statistics reports. Existing generated
files with the same names in `output/` are overwritten.

### 2. Search the collection

After building the index, run:

```powershell
python -m src.search_cli
```

Enter one query per prompt. For example:

```text
भारत
"भारत सरकार"
भारत NEAR/5 सरकार
```

The CLI displays matching document IDs and positions. Enter `exit` to stop.
Search terms must use the same normalized Hindi spelling as the indexed text.

- A single term returns its matching documents and positions.
- A quoted phrase, such as `"भारत सरकार"`, returns positions where all phrase
  terms occur consecutively and in order.
- `भारत NEAR/5 सरकार` matches the two terms in either order if no more than
  five tokens lie between them. The reported result contains the pair of
  positions for each match.

### 3. Optionally download the dataset

To fetch a fresh set of articles, first install `requests` as described above,
then run this command from the project folder:

```powershell
python download_dataset.py
```

The script writes files into `dataset/documents/` and can replace files with
matching names. Build the index again after downloading so the output reflects
the current dataset. The downloader reports if it could not collect the full
target of 100 articles.

## Module descriptions

### `download_dataset.py`

Optional dataset collection script. It calls the Hindi Wikipedia API, gets
article titles from a predefined set of Hindi categories, avoids duplicate
titles during collection, and requests plain-text article extracts. Articles
shorter than 100 characters and missing pages are skipped. It saves accepted
articles as UTF-8 files named `DOC1.txt`, `DOC2.txt`, and so on under
`dataset/documents/`, up to the target of 100 documents. It includes a short
delay between successful article downloads and reports download errors and
the final number collected. It requires `requests` and an internet connection;
it is not needed to build the index from the included dataset.

### `src/preprocess.py`

Provides the text preprocessing functions used throughout the project.
`tokenize(text)` normalizes a string to Unicode NFC, extracts Devanagari
sequences, and returns `(term, position)` pairs with positions starting at 1.
`preprocess_document(file_path)` reads a UTF-8 document and passes its contents
to `tokenize`. Non-Devanagari text is not indexed.

### `src/positional_index.py`

Provides `iter_document_postings(documents_folder)`, the input stream for index
construction. It finds and sorts the `.txt` files in the collection, raises a
`FileNotFoundError` if none are present, and processes one document at a time.
For each document it groups the preprocessed positions by term and yields the
document ID (the filename without `.txt`) with that document's term positions.
It does not retain postings for previously processed documents.

### `src/storage.py`

Writes and reads the on-disk index. `save_index(document_postings,
output_folder)` consumes the document-at-a-time stream and writes one JSON
record per term-document pair to `output/postings.jsonl`. While writing, it
keeps vocabulary metadata in memory: each term's CF, DF, and a list of byte
offsets for that term's posting records. CF is increased by the number of
occurrences in a document; DF is increased once for each document containing
the term. The vocabulary metadata is then saved to
`output/vocabulary.json`. The full collection postings are not accumulated in
memory.

`load_vocabulary(output_folder)` loads the saved vocabulary JSON into memory.
`read_posting(term, vocabulary, output_folder)` seeks to the term's byte
offsets in the postings file and reconstructs its document-to-positions
mapping. Search therefore reads postings from secondary storage as needed.

### `src/search.py`

Implements the query operations using `read_posting`. `search_word` returns a
term's postings or an empty result if the term is absent.
`search_phrase` finds consecutive terms in their given order by checking
adjacent token positions. `search_near` finds pairs of terms in the same
document within the requested number of intervening tokens, in either order.
`search_query` recognizes a quoted phrase, a query of the form
`term NEAR/k term`, or treats the input as a single-term query. Results map
document IDs to positions (or position pairs for `NEAR/k`).

### `src/search_cli.py`

Provides the interactive command-line search interface. It loads the saved
vocabulary once at startup, prompts for queries, calls `search_query`, and
prints matching documents and positions. The index must already have been
built. Type `exit` to close the prompt.

### `src/main.py`

Coordinates the build and report-generation workflow. It derives project,
dataset, and output paths from its own location, streams the documents through
the indexer into storage, loads the vocabulary, and runs five search checks.
The checks cover a positive single-term query, positive and negative exact
phrases, and positive and negative `NEAR/1` queries. Expected postings are
calculated from the source documents for the terms used in the checks.
It also writes the ten lowest-CF terms and their postings to
`output/rare_terms.txt`, and writes document count, vocabulary size, and total
indexed token count to `output/index_stats.txt`.

## Index format and memory use

- `output/vocabulary.json` stores each term's `cf`, `df`, and `offsets` (byte
  offsets into the postings file).
- `output/postings.jsonl` stores one JSON line per term-document pair. Each
  line contains the `doc_id` and that term's positions in the document.

During construction, only the current document's grouped positions and the
vocabulary metadata are held in memory; postings for documents already
processed remain on disk. During search, the vocabulary is loaded into memory
and only the requested postings records are read from disk.

## Generated output

Running `python -m src.main` creates or replaces:

- `output/vocabulary.json`: vocabulary metadata (CF, DF, and postings offsets).
- `output/postings.jsonl`: positional postings on disk.
- `output/test_results.txt`: five search checks, their status, and matching
  document positions.
- `output/rare_terms.txt`: ten terms with the lowest CF, their CF and DF, and
  corresponding positional postings.
- `output/index_stats.txt`: total documents, vocabulary size, and total indexed
  tokens.

The checked-in output currently reports 100 documents, a vocabulary of 11,531
terms, and 69,737 indexed tokens. These totals may change if the dataset is
replaced and the index rebuilt.
