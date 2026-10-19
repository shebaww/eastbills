from bs4 import BeautifulSoup
from pathlib import Path
import time
import requests
import re
from paths import kenya_pdfs, ksh_file
kenya_pdfs.mkdir(parents=True, exist_ok=True)


class PdfScraper():
    ## Only call if you want re-install every pdf file of the kenyan treasury bills
    def __init__(self, years=None):
        self.years = years
        self.url = self.scrape_pdf()
            
    def run(self):
        self.install_pdfs()
    
    def scrape_pdf(self):
        if not ksh_file.exists():
          raise ValueError(f"{ksh_file} does not exist. Please scrape page '--run' then run again.")
        with open(ksh_file) as file:
            content  = file.read()
            soup = BeautifulSoup(content, "lxml")
            
            links = soup.find_all("a", href=True)
            valid_links = []


    # As of Sep 09, 2026 The kenyan uploads website hosts their tbills in one page across multiple links of 91_day, 182_day, 364_day all leading back to the same pdf, so in pattern making 91_days is just the same as turning it into 91_day as they're going to be pointing to the same page


            for link in links:
              years = "|".join(str(y) for y in self.years)
              pattern = rf"^.*/91_day_historical_treasury_bill_results/.*({years})\.pdf" # Only scrappign 2024-2026 for my research paper
              if link["href"]:
                url = link["href"]
                if re.match(pattern, url, re.I):
                  valid_links.append(url)

        return valid_links

    def install_pdfs(self):
        print("Installing PDF files (You might need to wait a while)....")
        skipped = 0
        downloaded = 0
        for link in self.url: 
          ext = re.search(r".*\s*dated\s*(\d{2}.*\.pdf)", Path(link).name, re.I)
          if not ext:
            ext = re.search(r".*(\d{2}.*\.pdf)", Path(link).name, re.I)
          ext = ext.group(1)
          link_name = kenya_pdfs / ext
          if link_name.exists():
            skipped +=1
            continue
          try:
              response = requests.get(f"https://www.centralbank.go.ke{link}", timeout=100)
              response.raise_for_status()
              downloaded +=1
          except requests.RequestException as e:
              print(f"  -> Failed to download {link}: {e}")
              continue
          with open(link_name, "wb") as file:
             file.write(response.content)
             time.sleep(1)
        print(f"PDFs: {downloaded} downloaded, {skipped} skipped (already present)")
