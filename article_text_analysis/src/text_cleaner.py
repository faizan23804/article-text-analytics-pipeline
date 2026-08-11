"""
text_cleaner.py
----------------
Purpose: Take raw extracted article text and produce the different
"views" of that text that analyzer.py will need downstream:

  1. Raw sentences (for Average Sentence Length, Fog Index)
  2. Raw words, including stopwords (for the same readability formulas)
  3. Cleaned words — stopwords + punctuation removed (for sentiment
     scoring, Word Count, Complex Word Count, Syllable counting)

IMPORTANT DESIGN NOTE: this file does NOT compute Personal Pronouns.
That must be done on the ORIGINAL, uncleaned text — because words like
"I", "we", "us", "my" are typically present in stopword lists and would
be silently removed here. Personal Pronoun counting belongs in
analyzer.py, operating on the raw text directly, not on anything this
file produces.

spaCy is used ONLY for tokenization (splitting text into sentences and
words) — NOT for stopword removal. The actual stopword removal uses the
domain-specific StopWords files provided for this assignment, since
spaCy's built-in stopword list is generic and not tuned for financial
text.
"""

import sys
import os
import glob
import string
import spacy # type: ignore

from article_text_analysis.exceptions.exception import CustomException
from article_text_analysis.logger.logging import logging

# Load the spaCy model ONCE at import time, not inside every function call.
# Loading a language model is relatively expensive — doing it once and
# reusing the same `nlp` object across all 148 articles is far more
# efficient than reloading it per article.
nlp = spacy.load("en_core_web_sm")


def load_stopwords(stopwords_dir):
    """
    Reads every .txt file inside the given StopWords folder and combines
    them into a single set of lowercase stopwords.

    Handles a known gotcha with this assignment's provided files: some
    StopWords files are not plain UTF-8 encoded and will raise a
    UnicodeDecodeError if opened normally. We fall back to 'latin-1'
    encoding (which can decode any byte sequence without error) if UTF-8
    fails, rather than letting the whole pipeline crash over one file's
    encoding quirk.
    """
    stopwords = set()
    try:
        file_paths = glob.glob(os.path.join(stopwords_dir, "*.txt"))

        if not file_paths:
            logging.warning(f"No .txt files found in stopwords directory: {stopwords_dir}")

        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                logging.warning(
                    f"{os.path.basename(file_path)} was not UTF-8 encoded — "
                    f"retrying with latin-1 encoding."
                )
                with open(file_path, "r", encoding="latin-1") as f:
                    lines = f.readlines()

            for line in lines:
                # Some StopWords files use a "word | source" format
                # (pipe-separated) — we only want the word itself.
                word = line.strip().split("|")[0].strip().lower()
                if word:
                    stopwords.add(word)

        logging.info(f"Loaded {len(stopwords)} stopwords from {stopwords_dir}")
        return stopwords

    except Exception as e:
        raise CustomException(e, sys)


def get_raw_sentences(text):
    """
    Returns a list of sentence strings, using spaCy's sentence boundary
    detection (smarter than naively splitting on periods — handles
    things like "Mr. Smith" correctly).
    """
    try:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        return sentences
    except Exception as e:
        raise CustomException(e, sys)


def get_raw_words(text):
    """
    Returns a list of raw words from the text — INCLUDING stopwords,
    EXCLUDING pure punctuation and whitespace tokens. This is the word
    list used for readability formulas (Fog Index, Average Sentence
    Length), which care about raw sentence structure, not sentiment
    relevance.
    """
    try:
        doc = nlp(text)
        words = [
            token.text for token in doc
            if not token.is_punct and not token.is_space
        ]
        return words
    except Exception as e:
        raise CustomException(e, sys)


def get_cleaned_words(raw_words, stopwords_set):
    """
    Given a list of raw words (from get_raw_words), removes stopwords
    and strips any leftover punctuation characters attached to a word
    (e.g. "growth," -> "growth"). This is the word list used for
    sentiment scoring, Word Count, Complex Word Count, and Syllable
    counting.
    """
    try:
        cleaned = []
        for word in raw_words:
            # Strip punctuation characters that might still be attached
            # to a word even though the token itself wasn't PURE
            # punctuation (e.g. spaCy may keep "growth," as one token
            # in some edge cases).
            stripped = word.strip(string.punctuation)
            if not stripped:
                continue
            if stripped.lower() in stopwords_set:
                continue
            cleaned.append(stripped)
        return cleaned
    except Exception as e:
        raise CustomException(e, sys)


def clean_text(text, stopwords_set):
    """
    Convenience function that runs the full cleaning workflow on a
    single piece of text and returns everything analyzer.py will need,
    bundled together.
    """
    raw_sentences = get_raw_sentences(text)
    raw_words = get_raw_words(text)
    cleaned_words = get_cleaned_words(raw_words, stopwords_set)

    return {
        "raw_sentences": raw_sentences,
        "raw_words": raw_words,
        "cleaned_words": cleaned_words,
    }


if __name__ == "__main__":
    # Quick manual sanity check using a tiny inline example — no file
    # dependencies needed to verify the core logic works.
    sample_text = (
        "We predicted the next cross using our logistic regression model. "
        "It gave 91% accuracy on test data."
    )
    fake_stopwords = {"the", "a", "an", "on", "using"}

    result = clean_text(sample_text, fake_stopwords)
    print("RAW SENTENCES:", result["raw_sentences"])
    print("RAW WORDS:", result["raw_words"])
    print("CLEANED WORDS:", result["cleaned_words"])