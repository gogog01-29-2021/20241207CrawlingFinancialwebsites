cd C:\Users\kimseonghyun\Downloads\241207webcrawler
python -m venv venv
venv\Scripts\activate.bat

How colab things are working


How beautifulsoup working?
Error
1. Code was scrapping HTML
However The page was HTMOL

2.How is Beautifulsoupworking
selector

1.
Beautifulsoup to parse            
Always need css selector '[.download-list'


Selecnium can go bae on class name- cop Xpath
2.
Selenium parse more reasonably


3.<ul class="download-list">
Sets of Iterators


why it is not needed?


def extract_annual_report(soup: BeautifulSoup, config: dict) -> dict:
    """
    Extract the most recent annual report from the given tab.
    """
    rows = soup.select(config["rows"])
    logging.info(f"Found {len(rows)} rows in the tab.")
    
    for row in rows:
        try:
            # Extract the title and check if it's the Annual Report
            title_elem = row.select_one(config["title"])
            title = title_elem.text.strip() if title_elem else "N/A"
            if "Annual Report" not in title:
                continue
            
            # Extract the document link
            link_elem = row.select_one(config["link"])
            link = urljoin(BASE_URL, link_elem["href"]) if link_elem else "N/A"
            
            # Return the first matching annual report
            return {"title": title, "date": "N/A", "link": link}
        except Exception as e:
            logging.warning(f"Error extracting row: {e}")
            continue
    
    return None

def save_to_csv(data: list, filename: str):
    """
    Save the extracted data to a CSV file.
    """
    if not data:
        logging.warning("No data to save!")
        return

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["title", "date", "link"])
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Data successfully saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")

=================================================================
1.
Different config 
find main


2. 2024 2023 2022 