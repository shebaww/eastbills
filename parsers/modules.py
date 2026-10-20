import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
import pdfplumber
import os
import sys; from pathlib import Path
from paths import current_dir, root, data, scrapers, parsers, kenya_pdfs, ETH_CSV, KSH_CSV, MASTER_CSV, inflation, ETH_INF_CSV, KSH_INF_CSV, INF_MASTER_CSV, eth_fx_file, ksh_fx_file, ksh_fx_csv, eth_fx_csv, master_fx_csv
from parsers import ksh_methods
from parsers import eth_methods
from scrapers.inflation_rates import get 


class Parser():
    class fx_rates():
        def run(self):
            self.kenya()
            self.ethiopia()

        def kenya(self):
            print("Parsing Kenya FX Rates")
            with open(ksh_fx_file, "r") as file:
                content = file.read()
                soup = BeautifulSoup(content, "lxml")
                section = soup.find("table")
                my_section = section.find_all("tr")

                fx = []

                for row in my_section:
                  value = row.text
                  value.strip()
                  value = value.split("\n")
                  for i in value:
                    if i == "" or i == None:
                      continue
                  fx.append(value)

                df = pd.DataFrame(fx)
                df = df.iloc[:,[2, 3]]
                df.columns = ["Kenya Rate", "date"]
                df["Kenya Rate"] = pd.to_numeric(
                    df["Kenya Rate"].astype(str).str.strip(), errors="coerce"
                )
                df["date"] = pd.to_datetime(
                    df["date"].astype(str).str.strip(), errors="coerce"
                )
                df = df.dropna(subset=["Kenya Rate", "date"])
                df.dropna(axis=1, how='all', inplace=True)
                df = self._convert_to_monthly_rates(df)
                df = df[(df["date"].dt.day == 1) & (df["date"] >= "2024-08-01") & (df["date"] <= "2026-05-01")]
                df.reset_index(inplace=True, drop=True)
                df.to_csv(ksh_fx_csv)
                print(f"Finished Parsing Kenya Fx Rates Saved to: {ksh_fx_csv}")

        def ethiopia(self):
            print("Parsing Ethiopia FX Rates")
            with open(eth_fx_file, "r") as file:
                content = file.read()
                soup = BeautifulSoup(content, "lxml")
                section = soup.find("table")
                my_section = section.find_all("tr")

                fx = []

                for row in my_section:
                  value = row.text
                  value.strip()
                  value = value.split("\n")
                  for i in value:
                    if i == "" or i == None:
                      continue
                  fx.append(value)

                df = pd.DataFrame(fx)
                df = df.iloc[:,[2, 3]]
                df.columns = ["Ethiopia Rate", "date"]
                df["Ethiopia Rate"] = pd.to_numeric(
                    df["Ethiopia Rate"].astype(str).str.strip(), errors="coerce"
                )
                df["date"] = pd.to_datetime(
                    df["date"].astype(str).str.strip(), errors="coerce"
                )
                df = df.dropna(subset=["Ethiopia Rate", "date"])
                df.dropna(axis=1, how='all', inplace=True)
                df = self._convert_to_monthly_rates(df)
                df = df[(df["date"].dt.day == 1) & (df["date"] >= "2024-08-01") & (df["date"] <= "2026-05-01")]
                df.reset_index(drop=True, inplace=True)
                df.to_csv(eth_fx_csv)
                print(f"Finished Parsing Ethiopia Fx Rates Saved to: {eth_fx_csv}")
        
        def merge(self):
            print("Merging FX Rates...")
            if not os.path.exists(eth_fx_csv):
                print(f"Missing {eth_fx_csv}")
                answer = input("Would you want to repopulate it?(y/N): ").strip().lower()
                if answer == "y":
                    self.ethiopia()
                else:
                    raise FileNotFoundError(f"Please repopulate {eth_fx_csv}")
            if not os.path.exists(ksh_fx_csv):
                print(f"Missing {ksh_fx_csv}")
                answer = input("Would you want to repopulate it?(y/N): ").strip().lower()
                if answer == "y":
                    self.kenya()
                else:
                    raise FileNotFoundError(f"Please repopulate {ksh_fx_csv}")
            df_eth = pd.read_csv(eth_fx_csv, index_col=0)
            df_ksh = pd.read_csv(ksh_fx_csv, index_col=0)
            combined_df = pd.merge(df_eth, df_ksh, on="date", how="inner").reset_index(drop=True)
            combined_df.to_csv(master_fx_csv, index=False)
            print(f"Merged Files\nSaved to {master_fx_csv}")

        @staticmethod
        def _convert_to_monthly_rates(df: pd.DataFrame) -> pd.DataFrame:
          """Takes a multi-frequency FX rate DataFrame, aggregates it to 1 rate per month,

          and sets the Effective Date to the 1st of each month (YYYY-MM-01).
          """
          df = df.copy()
          df["date"] = pd.to_datetime(df["date"])
          df = df.sort_values("date")
          df = df.set_index("date")
          # 5. Resample to Month Start ('MS')
          # 'MS' automatically changes all dates in a month to the 1st (e.g., 2026-10-01)
          # .mean() averages out the bi-monthly/tri-monthly rates for that month.
          # (You can swap .mean() for .first() if you prefer picking the first rate of the month)
          monthly_df = df.resample("MS").mean().reset_index()

          return monthly_df


    class inflation():
        def run(self):
            self.ethiopia()
            self.kenya()

        MONTHS = {
            'jan': 1, 'feb': 2, 'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        def __init__(self):
            self.eth_pdfs = ["0.pdf", "1.pdf", "2.pdf", "3.pdf"]

        @classmethod
        def _month_num(cls, label):
            s = re.sub(r'efy\s*\d{4}', '', label.lower()).strip(' _-')
            for name in sorted(cls.MONTHS, key=len, reverse=True):
                if s.startswith(name):
                    return cls.MONTHS[name]
            return None

        @staticmethod
        def _parse_block(table):
            block = []
            for row in table:
                if not row or not row[0]:
                    continue
                label = row[0].strip()
                if re.search(r"issue no|was|^month", label, re.I):
                    continue
                try:
                    value = float(row[1])
                except (TypeError, ValueError, IndexError):
                    continue
                block.append((label, value))
            return block

        @classmethod
        def _assign_dates(cls, block):
            # Drop spurious first row: anchor followed by same-month row
            if len(block) > 1 and "EFY" in block[0][0]:
                if cls._month_num(block[0][0]) == cls._month_num(block[1][0]):
                    block = block[1:]

            anchor_label = block[-1][0]
            if re.search(r'EFY\s*(\d{4})', anchor_label).group(1) == None:
               raise ValueError("Error: Ciuld not find EFY Year for anchor date")
            efy_year = int(re.search(r'EFY\s*(\d{4})', anchor_label).group(1))
            month = cls._month_num(anchor_label)
            anchor_date = pd.Timestamp(year=efy_year + 8, month=month, day=1)

            n = len(block)
            return [
                (anchor_date + pd.DateOffset(months=i - (n - 1)), value)
                for i, (_, value) in enumerate(block)
            ]

        def ethiopia(self):
            records = []
            for pdf in self.eth_pdfs:
                with pdfplumber.open(inflation / pdf) as file:
                    tables = file.pages[4].extract_tables()
                for table in tables:
                    block = self._parse_block(table)
                    if block:
                        records.extend(self._assign_dates(block))

            df = (pd.DataFrame(records, columns=["date", "ethiopia"])
                    .drop_duplicates("date", keep="last")
                    .sort_values("date")
                    .reset_index(drop=True))

            df = df[(df["date"] >= "2024-08-01") & (df["date"] <= "2026-05-31")]
            df = df[["date", "ethiopia"]]
            df.to_csv(ETH_INF_CSV, index=False)
            print(f"File written at {ETH_INF_CSV}") 

        def kenya(self):
            df = pd.read_csv(KSH_INF_CSV)
            if "Kenya" in df.columns:
              print(KSH_INF_CSV, "Already parsed")
            else:
              df.reset_index(inplace=True, drop=True)
              df.columns = ["date","overall_cpi","Kenya","yoy_inflation","core_inflation","non_core_inflation"]
              df.to_csv(KSH_INF_CSV, index=False)
              print(f"File written at {KSH_INF_CSV}")
            # Always apply date filter
            df = pd.read_csv(KSH_INF_CSV)
            df = df[df["date"] >= "2024-08-01"]
            df.to_csv(KSH_INF_CSV, index=False)

        def merge(self):
            print("Merging Monthly Inflation Rates...")
            Get = get()
            self.kenya()
            if not os.path.exists(KSH_INF_CSV):
                print(f"Missing {KSH_INF_CSV}")
                answer = input("Would you want to repopulate it?(y/N): ").strip().lower()
                if answer == "y":
                    Get.kenya()
                else:
                    raise FileNotFoundError(f"Please repopulate {KSH_INF_CSV}")
            if not os.path.exists(ETH_INF_CSV):
                print(f"Missing {ETH_INF_CSV}")
                answer = input("Would you want to repopulate it?(y/N): ").strip().lower()
                if answer == "y":
                    Get.ethiopia()
                else:
                    raise FileNotFoundError(f"Please repopulate {ETH_INF_CSV}")
            inf_df_eth = pd.read_csv(ETH_INF_CSV)
            inf_df_ksh = pd.read_csv(KSH_INF_CSV)
            inf_combined_df = pd.merge(inf_df_eth, inf_df_ksh, on="date", how="outer")
            inf_combined_df.drop(columns=["overall_cpi", "yoy_inflation", "core_inflation", "non_core_inflation"], inplace=True)
            inf_combined_df.to_csv(INF_MASTER_CSV, index=False)
            print(f"Merged Files\nSaved to {INF_MASTER_CSV}")

    

    class tbills():
        def __init__(self):
            self.Write = Write_tocsv()

        def kenya(self):
            print("Parsing Kenyan T-Bills....")
            pdf_files = len([f for f in os.listdir(kenya_pdfs) if f.lower().endswith('.pdf')])
            if pdf_files < 10:
              raise FileNotFoundError("Please Populate More Pdf Files for kenyan tbill")
            # For tests
            # pdf_files = ["backup/test.pdf", "backup/rtest.pdf"]
            KPM = ksh_methods.KenyanParserMethods()
            KSH_CSV.unlink(missing_ok=True)
            print(f"Automatically Re-populating {KSH_CSV}")
            print("-"*60)
            for i, _ in enumerate(range(pdf_files), start=1):
              df = KPM.process_single_pdf()
              self.Write.pdf(df)
              print(f"\rParsing [{i}/{pdf_files}]", end="", flush=True)
            print(f"\nCompleted Parsing and Writing Kenyan PDF Files")
            


        def ethiopia(self):
            print("Parsing Ethiopian T-Bills....")
            EPM = eth_methods.EthiopianParserMethods()
            ETH_CSV.unlink(missing_ok=True)
            print(f"Automatically Re-populating {ETH_CSV}")
            print("-"*60)
            self.Write.html(EPM.scrape())
       
        def merge(self):
            print("Merging T-Bills...")
            if not os.path.exists(KSH_CSV):
                print(f"Missing {KSH_CSV}")
                answer = input("Would you want to repopulate it?(y/N): ").strip().lower()
                if answer == "y":
                    self.kenya()
                else:
                    raise FileNotFoundError(f"Please repopulate {KSH_CSV}")
            if not os.path.exists(ETH_CSV):
                print(f"Missing {ETH_CSV}")
                answer = input("Would you want to repopulate it?(y/N): ").strip().lower()
                if answer == "y":
                    self.ethiopia()
                else:
                    raise FileNotFoundError(f"Please repopulate {ETH_CSV}")
            df_eth = pd.read_csv(ETH_CSV)
            df_ksh = pd.read_csv(KSH_CSV)
            combined_df = pd.concat([df_eth, df_ksh], ignore_index=True)
            combined_df.to_csv(MASTER_CSV, index=False)
            print(f"Merged Files\nSaved to {MASTER_CSV}")

class Write_tocsv():
    def html(self, clean_table):
        eth_exists = os.path.exists(ETH_CSV)
        for df in clean_table:
          df.to_csv(
                    ETH_CSV,
                    index=False,
                    mode="a",
                    header=not eth_exists,
                    )
          eth_exists = True

    
    def pdf(self, df):
        if df is None or (hasattr(df, 'empty') and df.empty):
          return
        ksh_exists = os.path.exists(KSH_CSV)
        df.to_csv(
            KSH_CSV, 
            mode='a',    
            index=False,    
            header=not ksh_exists 
        )

    

