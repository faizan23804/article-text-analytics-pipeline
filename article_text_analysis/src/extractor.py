import requests
import sys
import os
from bs4 import BeautifulSoup  # type: ignore
import time
from pathlib import Path

from article_text_analysis.exceptions.exception import CustomException
from article_text_analysis.logger.logging import logging

# __file__ = the absolute path to THIS script, wherever it sits on disk.
# walk UP from this file's own location to the project root, so this
# script behaves identically no matter what folder happened to be

# extractor.py lives at: <PROJECT_ROOT>/article_text_analysis/src/extractor.py
# so we go up 3 levels: src -> article_text_analysis -> PROJECT_ROOT
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw_articles"

# Request headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}


def fetch_html(url, timeout=10):
    """
    Downloads the raw HTML of a given URL.
    Returns the HTML text, or None if the request failed.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        
        logging.error(f"Failed to fetch {url} | Reason: {e}")
        return None


def extract_article(html, url_id):
    """
    Receives raw HTML and URL_id,
    extracts the article title and body text.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
 
        title_tag = soup.find("h1", class_="entry-title")
        if title_tag is None:
            title_tag = soup.find("h1")
 
        if title_tag is None:
            logging.warning(f"[{url_id}] Could not find a title tag.")
            title = ""
        else:
            title = title_tag.get_text(strip=True)
 
        body_container = soup.find("div", class_="td-post-content")
        if body_container is None:
            body_container = soup.find("div", class_="td-main-content")
        if body_container is None:
            body_container = soup.find("article")
 
        if body_container is None:
            logging.warning(f"[{url_id}] Could not find article body container.")
            return title, None
 
        content_tags = body_container.find_all(["p", "li", "h1", "h2", "h3", "h4"])
 
        collected_tags = []
        for tag in content_tags:
            tag_text = tag.get_text(strip=True)
            if tag.name in ("h1", "h2", "h3", "h4") and tag_text.lower() in ("project snapshots", "summarize", "contact details"):
                logging.info(f"[{url_id}] Reached 'Project Snapshot' heading — stopping extraction here.")
                break
            collected_tags.append(tag_text)
 
        body_text = "\n".join(t for t in collected_tags if t) # "if t" filters out empty strings
 
        if not body_text:
            logging.warning(f"[{url_id}] Article body was empty after extraction.")
            return title, None
 
        return title, body_text
    except Exception as e:
        raise CustomException(e, sys)


def save_article(url_id, title, body_text, output_dir=None):
    """
    Saves the extracted title + body to a text file named {url_id}.txt
    """
    try:
        if output_dir is None:
            output_dir = DEFAULT_OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{url_id}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(title + "\n")
            f.write(body_text)
        logging.info(f"[{url_id}] Saved successfully to {file_path}")
    except Exception as e:
        raise CustomException(e, sys)


def process_url(url_id, url, delay=1):
    """
    Full pipeline for one URL: fetch -> extract -> save.
    Returns True if successful, False if it failed at any stage.
    """
    try:
        html = fetch_html(url)
        if html is None:
            return False

        title, body_text = extract_article(html, url_id)
        if body_text is None:
            return False

        save_article(url_id, title, body_text)

        time.sleep(delay)
        return True
       
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    test_url_id = "test001"
    test_url = "https://insights.blackcoffer.com/automated-job-data-import-and-management-solution-for-enhanced-efficiency/"

    success = process_url(test_url_id, test_url)
    if success:
        print(f"SUCCESS. Check data/raw_articles/{test_url_id}.txt")
    else:
        print("FAILED. Check the latest file in logs/ for details.")