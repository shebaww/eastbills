import requests
from paths import data, eth_file, ksh_file, eth_fx_file, ksh_fx_file

class WebScraper():
    def __init__(self):
        self.ksh_link = "https://www.centralbank.go.ke/bills-bonds/treasury-bills/"
        self.eth_link = "https://nbe.gov.et/treasury-bills/"
        self.ksh_fx_link = "https://huggingface.co/datasets/shebaww/un-treasury-eastafrican-fx-rates/raw/main/kenya_rates.html"
        self.eth_fx_link = "https://huggingface.co/datasets/shebaww/un-treasury-eastafrican-fx-rates/raw/main/ethiopia_rates.html"
    
    def run(self):
        print("Installing Pages....")
        if eth_file.exists():
          print(f"File already exist at {eth_file}")
          answer = input("Overwrite(y/N)?: ").strip().lower()
          if answer == "y":
            self.eth_scrape()
          else:
             print(f"Keeping existing {eth_file}")
        else:
          self.eth_scrape()
       
        if ksh_file.exists():
           print(f"File already exist at {ksh_file}")
           answer = input("Overwrite(y/N)?: ").strip().lower()
           if answer == "y":
             self.ksh_scrape()
           else:
             print(f"Keeping existing {ksh_file}")
        else:
          self.ksh_scrape()
    
        if eth_fx_file.exists():
          print(f"File already exist at {eth_fx_file}")
          answer = input("Overwrite(y/N)?: ").strip().lower()
          if answer == "y":
            self.eth_fx_scrape()
          else:
             print(f"Keeping existing {eth_fx_file}")
        else:
          self.eth_fx_scrape()
       
        if ksh_fx_file.exists():
           print(f"File already exist at {ksh_fx_file}")
           answer = input("Overwrite(y/N)?: ").strip().lower()
           if answer == "y":
             self.ksh_fx_scrape()
           else:
             print(f"Keeping existing {ksh_fx_file}")
        else:
          self.ksh_fx_scrape()



    def ksh_scrape(self):
        with open(ksh_file, "w") as file:
            response = requests.get(self.ksh_link, timeout=100)
            response.raise_for_status()
            file.write(response.text)
            print(f"Saved file to {ksh_file}")

    def eth_scrape(self):
        with open(eth_file, "w") as file:
            response = requests.get(self.eth_link, timeout=100)
            response.raise_for_status()
            file.write(response.text)
            print(f"Saved file to {eth_file}")

    def ksh_fx_scrape(self):
        with open(ksh_fx_file, "w") as file:
            response = requests.get(self.ksh_fx_link, timeout=100)
            response.raise_for_status()
            file.write(response.text)
            print(f"Saved file to {ksh_fx_file}")

    def eth_fx_scrape(self):
        with open(eth_fx_file, "w") as file:
            response = requests.get(self.eth_fx_link, timeout=100)
            response.raise_for_status()
            file.write(response.text)
            print(f"Saved file to {eth_fx_file}")






