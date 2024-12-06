import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("crawler.log", mode="w"),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://www.meiji.com/global/investors/results-presentations/"

# Define selectors
MEIJI_CONFIG = {
    "tabs": ".chapternav-items",  # Selector for year tabs
    "rows": "ul.download-list li",  # Selector for rows in each tab
    "title": "a span",             # Selector for document titles
    "link": "a",                   # Selector for document links
    'test': '.download-list'
}

def fetch_webpage(url: str) -> BeautifulSoup:
    """
    Fetch the webpage and return a BeautifulSoup object.
    Handles exceptions during HTTP requests.
    """
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def get_tabs(soup: BeautifulSoup, base_url: str) -> list:
    """
    Get the links for all year tabs (FYE 3/2025, FYE 3/2024, etc.).
    """
    tabs = soup.select(MEIJI_CONFIG["test"])

    lookfor = "Financial Statements"
    notlookfor = ["1Q", "2Q", "3Q"]

    tab_links = [tabs]
    a = [j.children for j in tabs]
    for y in a:
        b = [i for i in y if i != '\n']
        f = [i.select_one("a") for i in b if lookfor in i.select_one("span").text and not any(x in i.select_one("span").text for x in notlookfor)]
        if f:
            print(f[0]["href"])
            print(f[0].select_one("span").text)
            break 

    logging.info(f"Found {len(tab_links)} tabs.")
    return None


def main():
    """
    Main function to fetch, extract, validate, and save the latest Annual Report.
    """
    print("Script started.")

    # Fetch the main webpage
    soup = fetch_webpage(BASE_URL)
    if not soup:
        logging.error("Failed to fetch the main webpage.")
        return

    # Get links for all tabs (years)
    tab_links = get_tabs(soup, BASE_URL)
    if not tab_links:
        logging.warning("No tabs found.")
        return

    # Iterate through tabs to find the most recent annual report
    for tab_url in tab_links:
        logging.info(f"Checking tab: {tab_url}")
        tab_soup = fetch_webpage(tab_url)
        if not tab_soup:
            continue

        # Extract the annual report from the current tab
        report = extract_annual_report(tab_soup, MEIJI_CONFIG)
        if report:
            logging.info(f"Found Annual Report: {report['title']}")
            save_to_csv([report], "Latest.csv")
            return  # Stop after finding the first valid annual report

    logging.warning("No Annual Report found across all tabs.")

if __name__ == "__main__":
    main()
