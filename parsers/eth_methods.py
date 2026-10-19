import pandas as pd
import re
from bs4 import BeautifulSoup
import os
import csv
import sys; from pathlib import Path
from paths import data

class EthiopianParserMethods:
    def __init__(self):
          self.mega_list = self.get_tables()
          self.result = self.divide_tables()
          self.clean_table = self.parse_list()
          
    def scrape(self):
          return self.clean_table

    def get_tables(self):
          """This function parses all rows in a single table then adds it to a list of all tables so that there is a list for all rows in a table, a list for a table is all tables and all tables inside a list. It does so by iterating first through all the tables, then through all rows in a table, then through all values of a single row"""

          with open(f"{data}/NBE.gov.html") as file:
            content = file.read()
            soup = BeautifulSoup(content, "lxml")
            my_section = soup.find("div", class_="elementor-element elementor-element-631b990 elementor-widget elementor-widget-accordion")
            all_tables = my_section.find_all("tbody")
            tables_list = []
            for table in all_tables:
              table_rows = table.find_all("tr")
              single_table_list = []
              for row in table_rows:
                row_tds = row.find_all("td")
                row_tds = [c.get_text(strip=True) for c in row_tds]
                row_list = []
                for td in row_tds:
                  row_list.append(td)
                single_table_list.append(row_list)
              tables_list.append(single_table_list)
            return tables_list


    def divide_tables(self):
            result_tables = []
            seen_auctions = set()
            announcement_tables = []
            for table in self.mega_list:
                text = " ".join(" ".join(row) for row in table).lower()
                m = re.search(r"auction no[: ]+([\w/]+)", text)
                if m:
                    key = m.group(1)
                    if key in seen_auctions:
                        continue
                    seen_auctions.add(key)
                    result_tables.append(table)
        #    print(f"Announcement: {len(announcement_tables)}, Results: {len(result_tables)}")
        # Dont Really need anouncement table besides for comparing the amounts against results tables, because of this improperly documented website.
            return result_tables


    def parse_list(self):
           clean_table = []
           for table in self.result:
             cleaned = self.clean_info(table)
             if len(cleaned) < 2:
               continue
             clean_table.append({
                 "rows": cleaned,
                 "issue_number": self.get_issue_number(table),
                 "issue_date": self.get_issue_date(table),
             })
           
           df_cleaned_table = []

           for entry in clean_table:
             table = entry["rows"]
             header_index = None
             for i, row in enumerate(table):
               if any(re.search(r"\d{1,3}\s*DAYS?", c, re.I) for c in row):
                 header_index = i
                 break
             if header_index is None:
                 continue
             if not self.has_tenor_row(table): 
               continue
             df = pd.DataFrame(table[header_index + 1:])
             df = df.set_index(0)
             df.columns = table[header_index][1:] 
             df = df.T
             df.index.name = "Tenor"
             df = df.reset_index()
             if df.empty or len(df.columns) == 0:
               continue
             df = df[df["Tenor"].astype(str).str.strip() != ""]
             df.columns = [str(c).strip() for c in df.columns]
             df.rename(columns={df.columns[0]:"Tenor"}, inplace=True)
             df = self.normalize_columns(df)
             CANONICAL_FIELDS = [
             "Tenor",
             "Maturity Date",
             "Amount Offered (Millions)",
             "Bids Received (Millions)",
             "Total Amount Accepted (Millions)",
             "Weighted Average Yield (Annual in %)",
             "Weighted Average Price (Per 100)",
             "Issue Number",
             "Issue Date",
             "Country",
             "Currency",
                               ]
             df["Issue Number"] = entry["issue_number"]
             df["Issue Date"] = entry["issue_date"]
             df["Issue Date"] = pd.to_datetime(df["Issue Date"], format="mixed", errors="coerce").dt.strftime("%Y-%m-%d")
             df["Country"] = "Ethiopia"
             df["Currency"] = "ETB"
             df = df.reindex(columns=CANONICAL_FIELDS)
             df = df[df['Tenor'] != "TOTAL"]
             df = df.replace({"": pd.NA, "–": pd.NA})
             exclude_cols = ["Tenor", "Country", "Currency", "Issue Number", "Issue Date"]
             df = df.dropna(subset=[c for c in df.columns if c not in exclude_cols], how="all")
             df["Maturity Date"] = pd.to_datetime(df["Maturity Date"], format="mixed", errors="coerce").dt.strftime("%Y-%m-%d")
             df["Total Amount Accepted (Millions)"] = pd.to_numeric(
                  df["Total Amount Accepted (Millions)"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.strip(),
                  errors="coerce",
              )
             df["Amount Offered (Millions)"] = pd.to_numeric(
                  df["Amount Offered (Millions)"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.strip(),
                  errors="coerce",
              )

             df["Bids Received (Millions)"] = pd.to_numeric(
                  df["Bids Received (Millions)"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.strip(),
                  errors="coerce",
              )

             df_cleaned_table.append(df)

           return df_cleaned_table

    def has_tenor_row(self, table):
          for row in table[:10]:
              if any(re.search(r"\d{1,3}\s*DAYS?", c, re.I) for c in row):
                  return True
          return False

    def normalize_columns(self, df):
          """Maps various NBE header phrasings to a standardized set of column names."""
          rename_map = {}
          for col in df.columns:
              if not isinstance(col, str) or not col.strip():
                continue
              col_lower = col.lower().strip()
              
              if "maturity" in col_lower:
                  rename_map[col] = "Maturity Date"
              elif "amount offered" in col_lower:
                  rename_map[col] = "Amount Offered (Millions)"
              elif "bids received" in col_lower:
                  rename_map[col] = "Bids Received (Millions)"
              elif "total amount accepted" in col_lower:
                  rename_map[col] = "Total Amount Accepted (Millions)"
              elif "weighted average price" in col_lower:
                  rename_map[col] = "Weighted Average Price (Per 100)"
              elif "weighted average yield" in col_lower:
                  rename_map[col] = "Weighted Average Yield (Annual in %)"
                  
          df = df.rename(columns=rename_map)
          df = df.loc[:, ~df.columns.duplicated()]
          return df

    def get_issue_number(self, table):
          pattern = r"auction\s*no:?\s*(\d{3,4}(?:st|nd|rd|th)?/\d{1,2}),?"

          for row in table[0:5]:
            text = " ".join(row)
            m = re.search(pattern, text, re.I) 
            if m:
              return m.group(1)
          return None


    def get_issue_date(self, table):
          pattern = r"held on (\w*\s*)(\d{2}),?(\s*\d{4})"

          for row in table[0:5]:
            text = " ".join(row)
            m = re.search(pattern, text, re.I) 
            if m:
              month, date, year = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
              return f"{month} {date}, {year}"
          return None

    def clean_info(self, table):
          clean_table = []
          labels = r"competitive|note|maximum\s*price|minimum\s*price|maximum\s*yie(?:l)?d|national|results|auction|cut\s*off|source|minimum\s*yie(?:l)?d"
          for row in table:
            text = " ".join(row)
            if text.strip() == '':
              continue
            if re.search(labels, text, re.I):
              continue
            else:
              clean_table.append(row)
          return clean_table
