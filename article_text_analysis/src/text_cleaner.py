import sys
import os
import glob
import string
import spacy # type: ignore

from article_text_analysis.exceptions.exception import CustomException
from article_text_analysis.logger.logging import logging

nlp = spacy.load("en_core_web_sm")


def load_stopwords(stopwords_dir):
    """
    Reads every .txt file inside the given StopWords folder and combines
    them into a single set of lowercase stopwords.
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
                # StopWords files using a "word | source" format
                # (pipe-separated) — only wanting the word itself.
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
    detection.
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
    EXCLUDING pure punctuation and whitespace tokens. 
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
    and strips any leftover punctuation characters attached to a word.
    """
    try:
        cleaned = []
        for word in raw_words:
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
    single piece of text.
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