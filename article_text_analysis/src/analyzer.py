import sys
import os
import re
import string

from article_text_analysis.exceptions.exception import CustomException
from article_text_analysis.logger.logging import logging


def load_master_dictionary(positive_path, negative_path, stopwords_set):
    """
    Loads the Positive and Negative word dictionaries.Adds only those words in the dictionary if
    they are not found in the Stop Words Lists.
    """
    def _load_single_file(path):
        words = set()
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            logging.warning(f"{os.path.basename(path)} not UTF-8 — retrying with latin-1.")
            with open(path, "r", encoding="latin-1") as f:
                lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue  # skip blank lines
            word = line.lower()
            if word not in stopwords_set:
                words.add(word)
        return words

    try:
        positive_words = _load_single_file(positive_path)
        negative_words = _load_single_file(negative_path)
        logging.info(
            f"Loaded {len(positive_words)} positive words, "
            f"{len(negative_words)} negative words ."
        )
        return positive_words, negative_words
    except Exception as e:
        raise CustomException(e, sys)


def count_syllables(word):
    """
    Heuristic syllable counter: counts groups of consecutive vowels.
    """
    word = word.lower().strip(string.punctuation)
    if not word:
        return 0

    if word.endswith("es") or word.endswith("ed"):
        word = word[:-2]

    if not word:
        return 1     # return 1 if the entire word is just "es" or "ed" by itself.

    vowels = "aeiouy"
    syllables = 0
    prev_was_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllables += 1
        prev_was_vowel = is_vowel

    return max(syllables, 1)  # every real word has at least 1 syllable


def count_personal_pronouns(raw_text):
    """
    Counts occurrences of I, we, my, ours, us — matching most words
    case-insensitively, EXCEPT "us", which is matched in lowercase
    only, so "US" (the country) is correctly excluded.
    """
    try:
        pattern = re.compile(r"\b(I|we|my|ours|(?-i:us))\b", re.IGNORECASE)
        matches = pattern.findall(raw_text)
        return len(matches)
    except Exception as e:
        raise CustomException(e, sys)


def analyze_article(raw_text, raw_words, raw_sentences, cleaned_words,
                     positive_words, negative_words):
    """
    Computes all 13 variables for a single article and returns them
    as a dictionary, ready to be written into the output spreadsheet.
    """
    try:
        EPSILON = 0.000001  #avoids division by zero

        # Sentiment scores (CLEANED words)
        positive_score = sum(1 for w in cleaned_words if w.lower() in positive_words)
        negative_score = sum(1 for w in cleaned_words if w.lower() in negative_words)

        polarity_score = (positive_score - negative_score) / (
            (positive_score + negative_score) + EPSILON
        )

        word_count = len(cleaned_words)  # the assignment's "Word Count" variable
        subjectivity_score = (positive_score + negative_score) / (word_count + EPSILON)

        #  Readability (RAW words + sentences)
        raw_word_count = len(raw_words)
        raw_sentence_count = max(len(raw_sentences), 1)  # guard div-by-zero

        avg_sentence_length = raw_word_count / raw_sentence_count

        complex_words = [w for w in raw_words if count_syllables(w) > 2]
        complex_word_count = len(complex_words)
        pct_complex_words = complex_word_count / raw_word_count if raw_word_count else 0

        fog_index = 0.4 * (avg_sentence_length + pct_complex_words)

        # Same value as avg_sentence_length — computed once, reused,
        # per the assignment listing this as a separate output column.
        avg_words_per_sentence = avg_sentence_length

        # Word-level statistics (CLEANED words) 
        if cleaned_words:
            syllable_per_word = sum(count_syllables(w) for w in cleaned_words) / len(cleaned_words)
            avg_word_length = sum(len(w) for w in cleaned_words) / len(cleaned_words)
        else:
            syllable_per_word = 0
            avg_word_length = 0

        # Personal Pronouns (RAW original text) 
        personal_pronouns = count_personal_pronouns(raw_text)

        return {
            "POSITIVE SCORE": positive_score,
            "NEGATIVE SCORE": negative_score,
            "POLARITY SCORE": polarity_score,
            "SUBJECTIVITY SCORE": subjectivity_score,
            "AVG SENTENCE LENGTH": avg_sentence_length,
            "PERCENTAGE OF COMPLEX WORDS": pct_complex_words,
            "FOG INDEX": fog_index,
            "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,
            "COMPLEX WORD COUNT": complex_word_count,
            "WORD COUNT": word_count,
            "SYLLABLE PER WORD": syllable_per_word,
            "PERSONAL PRONOUNS": personal_pronouns,
            "AVG WORD LENGTH": avg_word_length,
        }

    except Exception as e:
        raise CustomException(e, sys)