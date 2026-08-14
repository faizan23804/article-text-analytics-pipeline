# Article Text Analytics Pipeline

An end-to-end NLP pipeline that scrapes article text from a list of URLs and computes 13 sentiment, readability, and text-structure metrics for each article — fully automated, from raw web page to a scored Excel output.

Built as a real-world-style data extraction and text analytics assignment, structured the way a production data pipeline would be: separated stages, resilient per-item error handling, and full logging/audit trail.

## What it does

Given a spreadsheet of article URLs, the pipeline:

1. **Extracts** the article title and body text from each URL — filtering out site navigation, headers, footers, and boilerplate contact/signature blocks
2. **Cleans** the text using spaCy tokenization and a domain-specific (financial-text) stopword list
3. **Analyzes** the cleaned text to compute 13 variables covering sentiment, readability, and word-level statistics
4. **Outputs** a single Excel file with one row per article, ready for further analysis

## The 13 computed variables

| Category | Variables |
|---|---|
| Sentiment | Positive Score, Negative Score, Polarity Score, Subjectivity Score |
| Readability | Avg Sentence Length, % Complex Words, Fog Index, Avg Words per Sentence |
| Text statistics | Complex Word Count, Word Count, Syllables per Word, Personal Pronouns, Avg Word Length |

Full formula definitions are documented inline in `analyzer.py`.

## Architecture

```
article-text-analytics-pipeline/
│
├── article_text_analysis/          # Installable Python package
│   ├── __init__.py
│   ├── exceptions/
│   │   └── exception.py            # Custom exception with file/line-level error context
│   ├── logger/
│   │   └── logging.py              # Timestamped, per-run logging configuration
│   └── src/
│       ├── extractor.py            # Fetches + parses a single article (BeautifulSoup)
│       ├── text_cleaner.py         # spaCy tokenization + stopword removal
│       ├── analyzer.py             # Computes all 13 variables
│       └── pipeline.py             # Orchestrates the full run across all URLs
│
├── data/
│   ├── raw_data/                   # input.xlsx (not included — see Setup)
│   └── raw_articles/               # Extracted article text files + provided dictionaries/stopwords
│
├── output/                         # Final output.xlsx lands here
├── logs/                           # One timestamped log file per run
├── main.py                         # Entry point — run this to process everything
├── setup.py
├── requirements.txt
└── .gitignore
```

**Design principle:** each module has exactly one job. `extractor.py` doesn't know cleaning or scoring exist; `pipeline.py` doesn't know how scraping works internally — it only calls already-tested functions from the other modules and stitches results together. This means a change to one stage (e.g. swapping the input format) never requires touching unrelated code.

## Tech stack

- **Python 3**
- **BeautifulSoup + requests** — HTML fetching and parsing
- **spaCy** (`en_core_web_sm`) — sentence/word tokenization
- **pandas + openpyxl** — Excel I/O
- Custom logging and exception-handling modules, built as an installable package (`pip install -e .`)

## Key design decisions worth knowing about

A few non-obvious choices, documented here rather than left implicit:

- **Raw vs. cleaned word lists are kept strictly separate.** Readability formulas (Fog Index, Avg Sentence Length) use the raw word/sentence lists, stopwords included — because they measure how the article actually reads. Sentiment and word-statistics formulas use the cleaned list, since they should only reflect meaningful content.
- **Personal Pronouns are counted from the original, uncleaned text**, not the cleaned word list — pronouns like "we," "us," and "my" are typically present in stopword lists and would otherwise be silently stripped before counting, always returning zero.
- **The "US" vs. "us" ambiguity is handled with a scoped-case regex** — matching "we," "my," "ours," "I" case-insensitively, while matching "us" only in lowercase, so the country abbreviation "US" is correctly excluded from the pronoun count.
- **A trailing "Contact Details" boilerplate block, present on every article from this source, is deliberately stripped** during extraction, so signature/contact information doesn't inflate word counts or skew readability scores.
- **All file paths are anchored to each script's own location** (`os.path.abspath(__file__)`), not the current working directory — so the pipeline behaves identically regardless of which folder it's run from.
- **Per-item failures never halt the batch.** Each URL is processed inside its own try/except at the orchestration level; an unexpected failure on one article is logged and the run continues, rather than losing progress on the remaining articles.

## Setup

```bash
# Clone and enter the project
git clone https://github.com/faizan23804/article-text-analytics-pipeline.git
cd article-text-analytics-pipeline

# Create and activate a virtual environment
conda create -p venv python=3.11
conda activate venv/    


# Install dependencies (includes an editable install of this package)
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Note:** `data/raw_data/input.xlsx`, the `StopWords` folder, and the `MasterDictionary` (positive/negative word lists) are not included in this repository, as they're provided assignment materials rather than original content. To run this pipeline, supply your own input spreadsheet (columns: `URL_ID`, `URL`) and stopword/dictionary files in the paths configured at the top of `pipeline.py`.

## Usage

```bash
python main.py
```

This processes every URL in `data/raw_data/input.xlsx` and writes the results to `output/output.xlsx`. Progress prints to the terminal; a detailed, timestamped log is written to `logs/` for every run.

## Output

`output/output.xlsx` contains one row per input URL, with the original `URL_ID` and `URL` columns preserved, followed by all 13 computed variables. If extraction fails for a given URL, its row is still included with blank metric values, so the output row count always matches the input — the specific failed IDs are reported in the run summary and logged for follow-up.

## Known limitations

- The syllable-counting heuristic (vowel-group counting, with `-es`/`-ed` endings excluded) follows the assignment's specified method rather than true linguistic pronunciation, so it can diverge slightly from actual spoken syllable counts on some words.
- Extraction selectors (HTML tags/classes) are tuned to this specific source site's structure and would need adjustment for a different domain.
- The Contact Details boilerplate filter matches on an exact heading string; a differently-formatted signature block on an edge-case article would not be caught.

