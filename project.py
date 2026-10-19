from scrapers import web_scrapper, pdf_scrapper, inflation_rates
from parsers import modules
from manipulation import graphs, analysis
import argparse

# Visual ASCII Art Banner
BANNER = r"""
 _____          _   _     _ _ _     
| ____|__ _ ___| |_| |__ (_) | |___ 
|  _| / _` / __| __| '_ \| | | / __|
| |__| (_| \__ \ |_| |_) | | | \__ \
|_____\__,_|___/\__|_.__/|_|_|_|___/

  East African Treasury Bill Analysis
======================================================================
"""


def main():
  print(BANNER)
  print("Tip: Run 'python project.py --help' to view available command options.\n")
  arger = argparse.ArgumentParser(description="Scrape and Merge East African Treasury Bill Data")
  arger.add_argument("--merge", action="store_true", help="Merge Kenya and Ethiopia CSV's (Inflation, Treasury Bills and FX Rates)")
  arger.add_argument("-r","--run", action="store_true", help="Scrape HTML files from Central Bank of Kenya and National Bank of Ethiopia and FX Rates from Hugging Face Data Source")
  arger.add_argument("-p","--pdfs",action="store_true", help="Download Kenyan Treasury Bill PDF's")
  arger.add_argument("--ethiopia", action="store_true", help="Parse Ethiopian T-Bills" )
  arger.add_argument("--kenya",action="store_true", help="Parse Kenyan T-Bills" )
  arger.add_argument("--inflation",action="store_true", help="Downloads Inflation rates for Ethiopia and Kenya and saves them in individual CSV Files" )
  arger.add_argument("--graphs",action="store_true", help="Graphs Some Yield Information" )
  arger.add_argument("--fx",action="store_true", help="Parses FX Rates for Ethiopia and Kenya and saves them in individual CSV Files" )
  arger.add_argument("--summary", "-s",action="store_true", help="Summarizes Countries Yield information" )
  arger.add_argument("--years", nargs="+", type=int, default=[2024, 2025, 2026],
                help="Which years to scrape/install (default: 2024 2025 2026) \n CAUTION: THIS OPTION ONLY INSTALLS FILES. IF YOU HAVE DIFFERENT YEAR PDF FILES IN 'data' THEY WILL BE USED AND PARSED. IF YOU DON'T WANT THEM USED DELETE EVERYTHING IN 'data' AND RE-INSTALL THE YEAR PDF FILES YOU ONLY WANT USED AND PARSED")

  args = arger.parse_args()
  years = args.years
  if args.run:
    run_webscraper()
  if args.ethiopia:
    run_ethiopia()
  if args.kenya:
    run_kenya(years)
  if args.merge:
    run_merge()
  if args.inflation:
    run_inflation()
  if args.fx:
    run_fx()
  if args.pdfs:
    run_pdfs(years)
  if args.graphs:
    run_graphs()
  if args.summary:
    run_summary()


def run_webscraper():
    WebScraper = web_scrapper.WebScraper()
    WebScraper.run()

def run_ethiopia():
    TbillParser = modules.Parser.tbills()
    TbillParser.ethiopia()

def run_kenya(years):
    PdfScraper = pdf_scrapper.PdfScraper(years=years)
    PdfScraper.run()
    TbillParser = modules.Parser.tbills()
    TbillParser.kenya()

def run_merge():
    TbillParser = modules.Parser.tbills()
    TbillParser.merge()
    InflationParser = modules.Parser.inflation()
    InflationParser.merge()
    FXParser = modules.Parser.fx_rates()
    FXParser.merge()

def run_graphs():
    illustrate = graphs.Illustrate()
    illustrate.run()

def run_inflation():
    InflationScraper = inflation_rates.get()
    InflationScraper.run()
    InflationParser = modules.Parser.inflation()
    InflationParser.run()

def run_pdfs(years):
    PdfScraper = pdf_scrapper.PdfScraper(years=years)
    PdfScraper.run()

def run_fx():
    FXParser = modules.Parser.fx_rates()
    FXParser.run()

def run_summary():
    Summary = analysis.Summary()
    Summary.run()

if __name__ == "__main__":
  main()
