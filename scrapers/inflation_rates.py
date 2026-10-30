import re
import requests
import os
import time
from paths import inflation, data, KSH_INF_CSV

class get:
    def __init__(self):
        # Only manually inserting links because scrapping everything is tough because evry file has some weird exception in finding using regex
        self.ethiopia_links = [
        "https://ess.gov.et/wp-content/uploads/2024/10/Consumer-price-indexAugust-2024-1.pdf",
        "https://ess.gov.et/wp-content/uploads/2024/09/CPI_aug_2023.pdf",
        "https://ess.gov.et/wp-content/uploads/2025/09/1.inflation-report-aug-efy-2017-final.pdf",
        "https://ess.gov.et/wp-content/uploads/2026/09/1.inflation-report-august-efy-2018-final.pdf"
        ]

        self.kenya_link = "https://github.com/yvvonelle/Kenya-CPI-and-Inflation-Analysis/raw/refs/heads/main/monthly_trend.csv"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ResearchBot/1.0 (contact: you@example.com)"
        })

    def ethiopia(self):
        print("Scraping Ethiopian Inflation Rate Pdf Files...")
        i = 0
        for url in self.ethiopia_links:
          filename = f"{inflation}/" + str(i) + ".pdf"
          i += 1
          if os.path.exists(filename):
            print(f"Skipping File, File already Exists at:{filename}")
            continue
          r = self.session.get(url, timeout=15)
          r.raise_for_status()
          with open(filename, "wb") as file:
              print(f"Writing {filename}")
              file.write(r.content)
        print("Finished Scraping Ethiopian Inflation rates as Pdf Files")

    def run(self):
        self.ethiopia()
        self.kenya()

    def kenya(self):
        print("Scraping Kenyan Inflation CSV File...")
        if os.path.exists(KSH_INF_CSV):
            print(f"Skipping File, File already Exists at:{KSH_INF_CSV}")
        else:
            with open(KSH_INF_CSV, "wb") as file:
              response = requests.get(self.kenya_link)
              response.raise_for_status()
              file.write(response.content)
              print(f"Finished Scraping Kenyan Inflation Rates. File written at {KSH_INF_CSV}")


