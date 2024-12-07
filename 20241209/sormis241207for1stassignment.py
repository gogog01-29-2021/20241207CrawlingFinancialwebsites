import requests
from bs4 import BeautifulSoup
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
    'download_list': '.download-list'
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

def get_tabs(soup: BeautifulSoup) -> list:
    """
    Get the links for all year tabs (FYE 3/2025, FYE 3/2024, etc.).
    """
    data = soup.select(MEIJI_CONFIG["download_list"])  # Get all the downloadable content

    lookfor = "Financial Statements"  # Look for the Financial Statements
    notlookfor = ["1Q", "2Q", "3Q"]  # Exclude quarterly reports

    if not data:
        logging.warning("No data found.")
        return None

    contents = [j.children for j in data]  # Get the children of each table of downloadable content
    for content in contents:
        usable_lines = [i for i in content if i != '\n']  # Remove empty lines
        # Get the link for the Financial Statements and exclude quarterly reports
        statement = [i.select_one("a") for i in usable_lines if lookfor in i.select_one("span").text and not any(x in i.select_one("span").text for x in notlookfor)]
        if statement:  # If found, return the link and the title, date can be extracted from the title
            logging.info(f"Found report: {statement[0].select_one('span').text}")
            return [statement[0]["href"], statement[0].select_one("span").text]

    return None

def save_to_csv(data: list, filename: str):
    """
    Save the extracted data to a CSV file.
    """
    if not data:
        logging.warning("No data to save!")
        return

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:  # Open the CSV file in write mode
            writer = csv.DictWriter(file, fieldnames=["title", "date", "link"])
            writer.writeheader()  # Write the header
            writer.writerow(data)  # Write the data as a single row
        logging.info(f"Data successfully saved to {filename}")
    except Exception as e:  # Catch any exception occurring during write
        logging.error(f"Error saving data to CSV: {e}")

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
    contents = get_tabs(soup)
    if not contents:
        logging.warning("No tabs found.")
        return

    # Extract the data and save to CSV
    tab_url, tab_title = contents

    data = {
        "title": tab_title,
        "date": tab_title.split("[")[-1].replace("]", "").replace("Revised on ", ""),  # Extract the date from the title
        "link": tab_url
    }

    save_to_csv(data, "Latest.csv")  # Save the data to a CSV file

if __name__ == "__main__":
    # Import Selenium and related modules
    import time
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from dataclasses import dataclass

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)  # Wait for 5 seconds for elements to appear
    driver.options = webdriver.ChromeOptions()
    driver.options.add_argument("--headless")  # Optional: Run in headless mode

    driver.get("https://www.china-tcm.com.cn/en/Investor/Announce")  # Open the webpage

    @dataclass
    class Release:
        title: str
        date: str
        link: str

    data: list[Release] = []

    driver.switch_to.frame("demo")  # Switch to the iframe

    def get_releases():
        time.sleep(3)  # Wait for 3 seconds for the page to load
        releases = driver.find_element(By.ID, "PressReleases")
        for release in releases.find_elements(By.CSS_SELECTOR, ".PressRelease"):
            if "opacity: 0" in release.get_attribute("style"):  # Skip hidden elements
                continue
            title = release.find_element(By.CSS_SELECTOR, ".PressRelease-NewsTitle").text
            date = release.find_element(By.CSS_SELECTOR, ".PressRelease-NewsDate").text
            link = release.find_element(By.CSS_SELECTOR, ".PressRelease-NewsTitle").get_attribute("href")
            data.append(Release(title, date, link))

    pages = driver.find_element(By.CSS_SELECTOR, ".Pages")
    buttons = pages.find_elements(By.TAG_NAME, "a")

    # Pagination handling
    last_button_with_number = int(buttons[-2].text)  # Keep track of the last button number
    while True:
        buttons = pages.find_elements(By.TAG_NAME, "a")  # Get all the buttons
        new_last_button_with_number = int(buttons[-2].text)  # Get the last button number
        get_releases()  # Get the releases
        if last_button_with_number > new_last_button_with_number:  # If the last button is less than the new last button, break
            break
        last_button_with_number = new_last_button_with_number  # Update the last button number
        buttons[-1].click()  # Click the next button

    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    save_to_csv([i.__dict__ for i in data], f"{current_time}.csv")
