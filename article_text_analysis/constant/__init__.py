import os
from pathlib import Path
import spacy # type: ignore


# __file__ = the absolute path to THIS script, wherever it sits on disk.
# constant lives at: <PROJECT_ROOT>/article_text_analysis/constant/__init__.py
# so we go up 3 levels: constant -> article_text_analysis -> PROJECT_ROOT
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw_articles" / "raw_texts"

# Request headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

# This is a boilerplate signature block —> it's almost certainly identical (or near-identical) at the
# bottom of every single one of your 148 articles, since it's the author's/company's standard
# info, not actual article content.
# So, we reliably detect and strip everything from that heading onward, for every article before saving
BOILER_PLATES = ("project snapshots", "summarize", "contact details")


# loading the English spaCy model.
nlp = spacy.load("en_core_web_sm")

INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw_data", "input.xlsx")
STOPWORDS_DIR = os.path.join(PROJECT_ROOT, "data", "raw_articles", "StopWords")
POSITIVE_DICT_PATH = os.path.join(PROJECT_ROOT, "data", "raw_articles", "dictionaries", "positive-words.txt")
NEGATIVE_DICT_PATH = os.path.join(PROJECT_ROOT, "data", "raw_articles", "dictionaries", "negative-words.txt")
RAW_ARTICLES_DIR = os.path.join(PROJECT_ROOT, "data", "raw_articles", "raw_texts")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output", "Output_Data_Structure.xlsx")

# The exact column order required by the assignment's output structure.
OUTPUT_COLUMNS = [
    "URL_ID", "URL",
    "POSITIVE SCORE", "NEGATIVE SCORE", "POLARITY SCORE", "SUBJECTIVITY SCORE",
    "AVG SENTENCE LENGTH", "PERCENTAGE OF COMPLEX WORDS", "FOG INDEX",
    "AVG NUMBER OF WORDS PER SENTENCE", "COMPLEX WORD COUNT", "WORD COUNT",
    "SYLLABLE PER WORD", "PERSONAL PRONOUNS", "AVG WORD LENGTH",
]
