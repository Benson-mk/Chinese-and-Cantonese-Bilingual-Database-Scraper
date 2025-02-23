import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# URL template: each id is appended as a query parameter
BASE_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/Search.aspx?id={}"

# Global counter and lock for thread-safe progress updates
progress_lock = threading.Lock()
completed = 0

def scrape_page(page_id):
    """
    Scrape a single page given the page id.

    Extracts the following fields:
      - 詞彙類別: from span with id "MainContent_repeaterRecord_lbl詞彙類別_0"
      - 粵語: from span with id "MainContent_repeaterRecord_lbl粵語詞彙_0"
      - 粵語拼音: from span with id "MainContent_repeaterRecord_lbl粵語拼音_0"
      - 聲調: from span with id "MainContent_repeaterRecord_lbl聲調_0"
      - 現代漢語詞彙1: from span with id "MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_0"
      - 現代漢語詞彙2: from span with id "MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_1"
      - 備註: from span with id "MainContent_repeaterRecord_lblRemark_0"
      
    Returns:
      A dictionary with the scraped data if successful; otherwise, returns None.
    """
    url = BASE_URL.format(page_id)
    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch id {page_id}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    def safe_extract(tag_id):
        tag = soup.find(id=tag_id)
        return tag.get_text(strip=True) if tag else ""

    record = {
        "id": page_id,
        "粵語": safe_extract("MainContent_repeaterRecord_lbl粵語詞彙_0"),
        "詞彙類別": safe_extract("MainContent_repeaterRecord_lbl詞彙類別_0"),
        "粵語拼音": safe_extract("MainContent_repeaterRecord_lbl粵語拼音_0"),
        "聲調": safe_extract("MainContent_repeaterRecord_lbl聲調_0"),
        "標準漢語1": safe_extract("MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_0"),
        "標準漢語2": safe_extract("MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_1"),
        "備註": safe_extract("MainContent_repeaterRecord_lblRemark_0"),
    }
    return record

def main():
    start_id = 1
    end_id = 22232
    total = end_id - start_id + 1
    results = []

    global completed

    # Using ThreadPoolExecutor to perform concurrent scraping.
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {executor.submit(scrape_page, i): i for i in range(start_id, end_id + 1)}
        
        for future in as_completed(future_to_id):
            record = future.result()
            with progress_lock:
                completed += 1
                # Print progress every 100 pages or when finished.
                if completed % 100 == 0 or completed == total:
                    print(f"Processed {completed}/{total} pages")
            if record is not None:
                results.append(record)

    # Sort results by id in ascending order
    results = sorted(results, key=lambda x: x["id"])

    # Write the full data to 'original.csv'
    original_columns = ["id", "粵語", "詞彙類別", "粵語拼音", "聲調", "標準漢語1", "標準漢語2","備註"]
    with open("original.csv", mode="w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=original_columns)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    # Write the filtered data to 'corresponding.csv' (dropping id, 詞彙類別, 粵語拼音, 聲調)
    corresponding_columns = ["粵語", "標準漢語1", "標準漢語2"]
    with open("corresponding.csv", mode="w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=corresponding_columns)
        writer.writeheader()
        for row in results:
            filtered_row = {col: row[col] for col in corresponding_columns}
            writer.writerow(filtered_row)

    print("Scraping complete. Files 'original.csv' and 'corresponding.csv' have been created.")

if __name__ == "__main__":
    main()
