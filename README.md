# Hindi Positional Index

This project builds a positional inverted index for Hindi text documents. It records each term's collection frequency (CF), document frequency (DF), and the positions where the term occurs in each document. It also supports word, exact phrase, and `NEAR/k` searches.

## Dataset

The project includes 100 Hindi Wikipedia article text files in `dataset/documents/`, named `DOC1.txt` through `DOC100.txt`. Files are UTF-8. The optional downloader, `download_dataset.py`, collects articles through the Hindi Wikipedia API and saves them in this folder.

The tokenizer normalizes text with Unicode NFC and indexes Devanagari sequences only. English and other scripts are ignored. Positions start at 1 and count the tokens extracted by the tokenizer.

## Project files

- `download_dataset.py` — downloads Hindi Wikipedia article text. Requires internet access and the `requests` package.

# Hindi Positional Index

## About the project

This project creates a positional index for Hindi text. It uses 100 Hindi
Wikipedia articles. For each indexed word, the program stores its collection
frequency (CF), document frequency (DF), document IDs, and word positions.

The index can search for one word, an exact phrase, or two words near each
other.

## Dataset

The text files are in `dataset/documents/` and are named `DOC1.txt` to
`DOC100.txt`. The `download_dataset.py` script can download Hindi Wikipedia
articles through the Wikipedia API. The included dataset can be used without
downloading it again.

The indexer normalizes text to Unicode NFC and indexes Devanagari text. Other
scripts, such as English, are not indexed. Positions start at 1 and count the
extracted words in each document.

## Project files

- `download_dataset.py`: Downloads articles from Hindi Wikipedia. It needs an
  internet connection and the `requests` package.
- `src/preprocess.py`: Reads a text file, normalizes it, extracts Devanagari
  words, and assigns positions.
- `src/positional_index.py`: Builds the index and calculates CF and DF for
  each word.
- `src/storage.py`: Saves and loads the vocabulary and postings.
- `src/search.py`: Provides single-word, exact-phrase, and `NEAR/k` search.
- `src/search_cli.py`: Provides an interactive search prompt.
- `src/main.py`: Builds the index and writes the example search results, rare
  terms, and index statistics.

## How the index is stored

The program writes two index files:

- `output/vocabulary.json` stores each word's CF, DF, and byte offset in the
  postings file. The vocabulary is loaded into memory for searching.
- `output/postings.jsonl` stores each word's document IDs and positions. The
  search code uses the offset to read a word's postings from this file.

During index creation, the current program first builds the full index in
memory, including postings, and then saves the postings to disk. Therefore,
postings are stored on disk for searching, but index creation does not keep
postings on disk the whole time.

## Requirements

- Python 3.8 or newer.
- The included text files in `dataset/documents/`.
- The `requests` package only if you want to download the dataset again.

Install `requests` if needed:

```bash
python -m pip install requests
```

## How to run

Run these commands from the project folder, where this README is located.

Build the index and create the output reports:

```bash
python -m src.main
```

Start interactive search after building the index:

```bash
python -m src.search_cli
```

Download the dataset again, if needed:

```bash
python download_dataset.py
```

The downloader writes files into `dataset/documents/` and can replace files
with the same names.

## Search examples

Use the same Hindi spelling as in the indexed text.

```text
भारत
"भारत सरकार"
भारत NEAR/5 सरकार
```

The phrase search finds consecutive words in the same order. `NEAR/5` finds
the two words when they have up to five intervening indexed words, in either
order.

## Output files

- `output/vocabulary.json`: Vocabulary, CF, DF, and postings offsets.
- `output/postings.jsonl`: Positional postings for all indexed words.
- `output/test_results.txt`: Results of five automated search checks. Expected
  results are calculated from the source documents and compared with actual
  indexed search results. Each case is marked PASS or FAIL.
- `output/rare_terms.txt`: Ten words with the lowest CF, their CF and DF, and
  their positional postings.
- `output/index_stats.txt`: Number of documents, vocabulary size, and total
  indexed tokens.

The current output reports 100 documents, a vocabulary of 11,531 words, and
69,737 indexed tokens. These values can change if the dataset changes.
