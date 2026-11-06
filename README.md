# Hindi Positional Index

This project builds a positional inverted index for Hindi text from 100 Hindi
Wikipedia article text files. For every indexed term, it records collection
frequency (CF), document frequency (DF), and the documents and token positions
where the term occurs. It supports single-term, exact-phrase, and `NEAR/k`
searches.

## Dataset and tokenization

The included UTF-8 documents are in `dataset/documents/`, named `DOC1.txt`
through `DOC100.txt`. The optional `download_dataset.py` script fetches Hindi
Wikipedia article text using the Wikipedia API and writes documents to that
folder. It requires an internet connection and the `requests` package.

The tokenizer normalizes text to Unicode NFC and extracts Devanagari sequences;
other scripts are ignored. Positions start at 1 and count the extracted tokens
in each document.

## Project files

- `download_dataset.py` downloads Hindi Wikipedia articles.
- `src/preprocess.py` normalizes document text, extracts Devanagari tokens, and
  assigns token positions.
- `src/positional_index.py` processes one document at a time and yields that
  document's term positions.
- `src/storage.py` streams each document's postings to disk while keeping only
  vocabulary statistics and postings offsets in memory; it also reads
  individual term postings.
- `src/search.py` implements single-term, exact-phrase, and `NEAR/k` searches.
- `src/search_cli.py` provides an interactive search prompt.
- `src/main.py` builds and saves the index, runs five search checks, and
  generates the rare-term and statistics reports.
- `dataset/documents/` contains the input documents.
- `output/` contains the generated index files and reports.

## Index format and storage

The index is saved in two files:

- `output/vocabulary.json` contains each term's CF, DF, and byte offsets into the
  postings file. Search loads this vocabulary into memory.
- `output/postings.jsonl` contains one JSON record per term and document, with
  that term's positions in the document. The in-memory vocabulary stores each
  term's CF, DF, and the byte offsets of its posting records. Search seeks to
  those offsets and reads the term's postings from disk. During construction,
  only the current document's term positions and the vocabulary are held in
  memory; the complete postings list is never accumulated in memory.

## Requirements

- Python 3.8 or newer.
- The included documents in `dataset/documents/`.
- The `requests` package only when downloading the dataset.

To install the optional downloader dependency:

```bash
python -m pip install requests
```

## Run the project

Run commands from the project folder (the folder containing this README).

Build the index and regenerate the reports:

```bash
python -m src.main
```

Start interactive search after building the index:

```bash
python -m src.search_cli
```

Download the dataset again if needed:

```bash
python download_dataset.py
```

The downloader writes into `dataset/documents/` and may replace files with
matching names.

## Search examples

Use the same Hindi spelling as in the indexed text:

```text
भारत
"भारत सरकार"
भारत NEAR/5 सरकार
```

An exact phrase matches consecutive tokens in the given order. `NEAR/5`
matches the two terms when they are no more than five intervening tokens apart,
in either order.

## Generated output

- `output/vocabulary.json`: vocabulary data saved as JSON, including CF, DF,
  and the byte offsets of the term's posting records.
- `output/postings.jsonl`: positional postings stored on disk.
- `output/test_results.txt`: five automated search checks with expected and
  actual matching documents and positions.
- `output/rare_terms.txt`: ten terms with the lowest CF, their CF and DF, and
  their positional postings.
- `output/index_stats.txt`: document count, vocabulary size, and total indexed
  token count.

The checked-in output currently reports 100 documents, a vocabulary of 11,531
terms, and 69,737 indexed tokens. These totals may change if the dataset
changes and the index is rebuilt.
