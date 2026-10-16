import os
import csv
import pdfplumber
import re
from pypdf import PdfReader
import pandas as pd
from pathlib import Path
from paths import kenya_pdfs

class KenyanParserMethods:
    def __init__(self):
        self.pdf_files = [f for f in os.listdir(kenya_pdfs) if f.lower().endswith('.pdf')]
        # For tests
        # self.pdf_files = ["backup/test.pdf", "backup/rtest.pdf"]
        self.index = 0
        self.filepath = None

    def process_single_pdf(self):
        self.filepath = f"{kenya_pdfs}/{self.pdf_files[self.index]}"
        try:
          table = self.grab_tables()
          issue_no = self.grab_issue_number()
          issue_date = self.grab_issue_date()
          self.index += 1
          return self.pd_parser(table, issue_no, issue_date)

        except Exception as e:
                print(f"  -> Error processing {self.filepath}: {e}")
                return None


    def grab_issue_number(self):
        reader = PdfReader(self.filepath)
        page = reader.pages[0]
        text = page.extract_text()
        pattern = r"bills issues (\d{4}/\d{3})+, (\d{4}/\d{3})+ & (\d{4}/\d{3})+.*dated"
        issue_no = []
        if i := re.search(pattern, text, re.I):
          issue_no.append(i.group(1))
          issue_no.append(i.group(2))
          issue_no.append(i.group(3))
          return issue_no

    def grab_issue_date(self):
        reader = PdfReader(self.filepath)
        page = reader.pages[0]
        text = page.extract_text()
        pattern = r"dated (\d{2}/\d{2}/\d{4})+"
        issue_no = []
        if issue_date := re.search(pattern, text, re.I):
          return issue_date.group(1)

    def grab_tables(self):
        with pdfplumber.open(self.filepath) as file:
          i = file.pages[0]
          mega_list =[]
          table = i.extract_tables()
          outcome_table = table[0]
          for rows in outcome_table:
            csv_row = []
            if "ISIN" in rows:
              continue
            for values in rows:
              csv_row.append(values)
            mega_list.append(csv_row)
        return mega_list

    def pd_parser(self, table, issue_no, issue_date):
      df = pd.DataFrame(table[1:], columns=table[0])
      df.columns = df.columns.str.strip()
      metric_col = df.columns[0]
      if not metric_col:
        df = df.rename(columns={metric_col:"Tenor"})
        metric_col = "Tenor"
      df = df.set_index(metric_col)
      df = df.T
      df = df.reset_index()
      df = df.rename(columns={df.columns[0]: "Tenor"})
      tenor_suffix = df["Tenor"].str.extract(r"(\d+)")[0].str.zfill(3)  
      issue_map = {"091": issue_no[0], "182": issue_no[1], "364": issue_no[2]}
      df = df[df['Tenor'] != "TOTAL"]
      df.columns = df.iloc[0]
      df = df[1:]
      df = df.rename(columns={df.columns[0]: "Tenor"})
      df["Issue Date"] = issue_date
      df["Issue Date"] = pd.to_datetime(df["Issue Date"], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
      df["Issue Number"] = tenor_suffix.map(issue_map)
      df["Country"] = "Kenya"
      df["Currency"] = "Kshs"
      df = df.drop(
        columns=[
            "Performance Rate (%)",
            "Rollover / Redemptions",
            "Market Weighted Average Interest\nRate",
            "New Borrowing/Net Repayment",
            "Of which: Competitive bids",
            ": Non-competitive bids",
            "Purpose / Application of Funds:",
            "Bid-to-Cover Ratio",
        ]
    )
      if "Due Date" in df.columns:
            df["Due Date"] = pd.to_datetime(df["Due Date"], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
      df.columns = df.columns.str.replace(r'\n', ' ', regex=True).str.strip()
      
      for col in df.columns:
        if col not in ["Tenor", "Due Date", "Issue Number", "Issue Date", "Country", "Currency", ""]:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[^\d.-]", "", regex=True),
                errors="coerce"
            )
      df = df.rename(columns={
                          df.columns[1]: "Maturity Date",
                          df.columns[2]: "Amount Offered (Millions)",
                          df.columns[3]: "Bids Received (Millions)",
                          df.columns[4]: "Total Amount Accepted (Millions)",
                          df.columns[5]: "Weighted Average Yield (Annual in %)",
                          df.columns[6]: "Weighted Average Price (Per 100)",
        })
      df = df.rename(columns={df.columns[0]: "Tenor"})
      return df
