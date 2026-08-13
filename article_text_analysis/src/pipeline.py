import sys
import os
import pandas as pd # type: ignore
from pathlib import Path

from article_text_analysis.exceptions.exception import CustomException
from article_text_analysis.logger.logging import logging
from article_text_analysis.src.extractor import process_url
from article_text_analysis.src.text_cleaner import (
    load_stopwords,
    get_raw_sentences,
    get_raw_words,
    get_cleaned_words,
)
from article_text_analysis.src.analyzer import (
    load_master_dictionary,
    analyze_article,
)
from article_text_analysis.constant import *




# Empty placeholder row used when a URL fails extraction, so the output
# still has one row per input URL_ID — just with blank metric values

BLANK_METRICS = {col: None for col in OUTPUT_COLUMNS if col not in ("URL_ID", "URL")}


def run_full_pipeline(input_path=None, output_path=None, delay=1):
    try:
        input_path = INPUT_PATH
        output_path = OUTPUT_PATH

        df = pd.read_excel(input_path)
        total = len(df)
        logging.info(f"Starting full pipeline run on {total} URLs.")

        
        stopwords_set = load_stopwords(STOPWORDS_DIR)
        positive_words, negative_words = load_master_dictionary(
            POSITIVE_DICT_PATH, NEGATIVE_DICT_PATH, stopwords_set
        )
        logging.info(
            f"Loaded {len(stopwords_set)} stopwords, "
            f"{len(positive_words)} positive / {len(negative_words)} negative words."
        )

        results = []
        success_count = 0
        failed_ids = []

        for row in df.itertuples(index=False):
            url_id = str(row.URL_ID)
            url = str(row.URL)

            try:
                extracted_ok = process_url(url_id, url, delay=delay)

                if not extracted_ok:
                    logging.warning(f"[{url_id}] Extraction failed — row will have blank metrics.")
                    results.append({"URL_ID": url_id, "URL": url, **BLANK_METRICS})
                    failed_ids.append(url_id)
                    print(f"[{success_count + len(failed_ids)}/{total}] {url_id} -> EXTRACTION FAILED")
                    continue

                # Read back the just-saved raw article text
                article_path = os.path.join(RAW_ARTICLES_DIR, f"{url_id}.txt")
                with open(article_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()

                raw_sentences = get_raw_sentences(raw_text)
                raw_words = get_raw_words(raw_text)
                cleaned_words = get_cleaned_words(raw_words, stopwords_set)

                metrics = analyze_article(
                    raw_text, raw_words, raw_sentences, cleaned_words,
                    positive_words, negative_words
                )

                results.append({"URL_ID": url_id, "URL": url, **metrics})
                success_count += 1
                print(f"[{success_count + len(failed_ids)}/{total}] {url_id} -> OK")

            except CustomException as e:
              
                logging.error(f"[{url_id}] Unexpected failure during processing: {e}")
                results.append({"URL_ID": url_id, "URL": url, **BLANK_METRICS})
                failed_ids.append(url_id)
                print(f"[{success_count + len(failed_ids)}/{total}] {url_id} -> UNEXPECTED FAILURE")

        # final output
        output_df = pd.DataFrame(results, columns=OUTPUT_COLUMNS)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_df.to_excel(output_path, index=False)

        summary = {
            "total": total,
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids,
            "output_path": output_path,
        }

        logging.info(
            f"Pipeline run complete. Success: {success_count}/{total}. "
            f"Failed: {len(failed_ids)} -> {failed_ids}. Output written to {output_path}"
        )

        return summary

    except Exception as e:
        raise CustomException(e, sys)