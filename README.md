# East African Treasury Bill Data Scraper & Analysis

A Python command-line tool that automates the collection, parsing, merging, and analysis of Treasury Bill data from the **Central Bank of Kenya (CBK)** and the **National Bank of Ethiopia (NBE)**. The tool also collects inflation rates and FX (foreign exchange) rate data for both countries, merges everything into unified CSV files, and generates publication-ready charts for research and analysis.

Demo Link: https://youtu.be/GKdaQVwDZIQ

---

## Features

- Scrapes HTML pages from CBK, NBE, and a Hugging Face FX rate dataset
- Automatically extracts and downloads targeted Kenyan T-Bill PDF files
- Parses Ethiopian and Kenyan financial data from HTML and PDF sources
- Scrapes and parses inflation rate data for both countries (Ethiopia from PDF reports, Kenya from CSV)
- Scrapes and parses monthly FX rates for both countries
- Combines cleaned datasets into individual CSV files and merged master CSV files
- Calculates weighted-average monthly yields, yield spreads, local real yields (inflation-adjusted), and FX-adjusted real yields
- Generates publication-ready vector PDF charts (nominal yields, yield spreads, real yields, inflation, FX rates)
- Produces a summary statistics table across both countries
- CLI built with `argparse` for easy command-line control

---

## Data Pipeline Overview

The tool is organized into a multi-stage pipeline. Each stage can be run independently or chained together:

```
Scraping → Parsing → Merging → Analysis → Graphs/Summary
```

### Stage 1: Scraping

| Source | Data | Scraper |
|--------|------|---------|
| CBK treasury bills page | Kenyan T-Bill HTML | `scrapers/web_scrapper.py` → `WebScraper.ksh_scrape()` |
| NBE treasury bills page | Ethiopian T-Bill HTML | `scrapers/web_scrapper.py` → `WebScraper.eth_scrape()` |
| Hugging Face dataset | Kenya & Ethiopia FX rate HTML | `scrapers/web_scrapper.py` → `WebScraper.ksh_fx_scrape()` / `eth_fx_scrape()` |
| CBK PDF links | Kenyan T-Bill result PDFs | `scrapers/pdf_scrapper.py` → `PdfScraper` |
| ESS (Ethiopia Statistical Service) | Ethiopian inflation report PDFs | `scrapers/inflation_rates.py` → `get.ethiopia()` |
| GitHub dataset | Kenyan CPI & inflation CSV | `scrapers/inflation_rates.py` → `get.kenya()` |

### Stage 2: Parsing

| Data | Parser |
|------|--------|
| Ethiopian T-Bill HTML → CSV | `parsers/eth_methods.py` → `EthiopianParserMethods` |
| Kenyan T-Bill PDFs → CSV | `parsers/ksh_methods.py` → `KenyanParserMethods` |
| Ethiopian inflation PDFs → CSV | `parsers/modules.py` → `Parser.inflation.ethiopia()` |
| Kenyan inflation CSV → normalized CSV | `parsers/modules.py` → `Parser.inflation.kenya()` |
| Kenya & Ethiopia FX rate HTML → CSV | `parsers/modules.py` → `Parser.fx_rates.kenya()` / `.ethiopia()` |

### Stage 3: Merging

| Merge | Output File |
|-------|-------------|
| Kenya + Ethiopia T-Bills | `data/master.csv` |
| Kenya + Ethiopia inflation | `data/master_inflation.csv` |
| Kenya + Ethiopia FX rates | `data/master_fx_rates.csv` |

### Stage 4: Analysis & Visualization

| Analysis | Description |
|----------|-------------|
| Monthly weighted-average yields | Yield per tenor, weighted by amount accepted |
| Yield spreads | Kenya minus Ethiopia, per tenor |
| Local real yields | Nominal yield minus annualized inflation (3-month moving average) |
| FX-adjusted real yields | Local real yield minus annualized FX depreciation (3-month moving average) |
| Summary statistics | Descriptive statistics (count, mean, std, min, max, quartiles) per country |

All charts are saved as vector PDFs to `data/results/`.

---

## Project Structure

```
tbill-scrappers/
├── project.py                    # Main CLI entry point
├── paths.py                      # All file paths and directory definitions
├── requirements.txt              # Python dependencies
├── scrapers/
│   ├── __init__.py
│   ├── web_scrapper.py           # Scrapes HTML pages (CBK, NBE, FX rates)
│   ├── pdf_scrapper.py           # Downloads Kenyan T-Bill PDF files
│   └── inflation_rates.py        # Scrapes inflation data (Ethiopia PDFs, Kenya CSV)
├── parsers/
│   ├── __init__.py
│   ├── modules.py                # Parser orchestration (tbills, inflation, fx_rates, Write_tocsv)
│   ├── eth_methods.py            # Ethiopian T-Bill HTML parsing logic
│   └── ksh_methods.py            # Kenyan T-Bill PDF parsing logic
├── manipulation/
│   ├── analysis.py               # Financial calculations & summary statistics
│   └── graphs.py                 # Matplotlib chart generation
└── data/                         # All output data (created at runtime)
    ├── kenya-pdfs/               # Downloaded Kenyan T-Bill PDFs
    ├── inflation_rate_pdfs/      # Downloaded Ethiopian inflation report PDFs
    ├── results/                  # Generated charts (PDF) and summary CSV
    ├── CBK.gov.html              # Scraped Kenyan T-Bill page
    ├── NBE.gov.html              # Scraped Ethiopian T-Bill page
    ├── kenya_fx_rates.html       # Scraped Kenya FX rate HTML
    ├── ethiopia_fx_rates.html    # Scraped Ethiopia FX rate HTML
    ├── ethiopian-tbills.csv       # Parsed Ethiopian T-Bill data
    ├── kenyan-tbills.csv          # Parsed Kenyan T-Bill data
    ├── master.csv                # Merged T-Bill data (both countries)
    ├── ethiopian_inflation_rates.csv
    ├── kenyan_inflation_rates.csv
    ├── master_inflation.csv      # Merged inflation data (both countries)
    ├── kenya_fx_rates.csv
    ├── ethiopia_fx_rates.csv
    └── master_fx_rates.csv       # Merged FX rate data (both countries)
```

---

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/shebaww/tbill-scrapper.git
cd tbill-scrapper
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate    # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the project script with Python. To view all available options:

```bash
python project.py --help
```

### CLI Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--run` | `-r` | Scrape all HTML pages (CBK, NBE, FX rates from Hugging Face) |
| `--pdfs` | `-p` | Download Kenyan T-Bill PDF result files |
| `--ethiopia` | | Parse Ethiopian T-Bills from scraped HTML into CSV |
| `--kenya` | | Download Kenyan PDFs and parse them into CSV |
| `--inflation` | | Download and parse inflation data for both countries |
| `--fx` | | Parse FX rate HTML files into CSV |
| `--merge` | | Merge all datasets (T-Bills, inflation, FX rates) into master CSVs |
| `--graphs` | | Generate all charts and save as PDFs to `data/results/` |
| `--summary` | `-s` | Generate summary statistics table |
| `--years` | | Specify which years to scrape/install (default: 2024 2025 2026) |

### Important Notes

**`--years` and local data:** The `--years` option controls which PDF files are downloaded and filtered. If you have older or different year PDF files already stored in `data/kenya-pdfs/`, they may still be referenced during parsing. For a clean run with only specific years, clear the `data/` directory before executing your command.

**Execution order matters:** The flags are processed in the order listed above. For a full pipeline run from scratch:

```bash
python project.py --run --kenya --ethiopia --inflation --fx --merge --graphs --summary
```

**Merge prompts:** The merge operations may prompt you to repopulate missing CSV files interactively. Ensure the individual country CSVs exist before merging, or the tool will ask whether to regenerate them.

---

## Example Commands

Scrape and parse Kenyan T-Bills for 2024:

```bash
python project.py --kenya --years 2024
```

Scrape only the HTML pages (no parsing):

```bash
python project.py --run
```

Download Kenyan T-Bill PDFs for specific years:

```bash
python project.py --pdfs --years 2024 2025
```

Parse Ethiopian T-Bills from already-scraped HTML:

```bash
python project.py --ethiopia
```

Download and parse inflation data for both countries:

```bash
python project.py --inflation
```

Parse FX rate HTML files into CSVs:

```bash
python project.py --fx
```

Merge all datasets (requires prior parsing):

```bash
python project.py --merge
```

Generate all charts (requires merged data):

```bash
python project.py --graphs
```

Generate summary statistics:

```bash
python project.py --summary
```

Full pipeline from scratch:

```bash
python project.py --run --kenya --ethiopia --inflation --fx --merge --graphs --summary
```

---

## Output Files

### T-Bill Data

| File | Description |
|------|-------------|
| `data/ethiopian-tbills.csv` | Parsed Ethiopian T-Bill auctions |
| `data/kenyan-tbills.csv` | Parsed Kenyan T-Bill auctions |
| `data/master.csv` | Merged T-Bill data (both countries) |

### Inflation Data

| File | Description |
|------|-------------|
| `data/ethiopian_inflation_rates.csv` | Ethiopian monthly inflation |
| `data/kenyan_inflation_rates.csv` | Kenyan monthly inflation |
| `data/master_inflation.csv` | Merged inflation data (both countries) |

### FX Rate Data

| File | Description |
|------|-------------|
| `data/kenya_fx_rates.csv` | Monthly Kenya FX rates |
| `data/ethiopia_fx_rates.csv` | Monthly Ethiopia FX rates |
| `data/master_fx_rates.csv` | Merged FX rate data (both countries) |

### Charts (saved to `data/results/`)

| File | Description |
|------|-------------|
| `time-series-yield-curve.pdf` | Nominal yield curves, Ethiopia and Kenya side-by-side |
| `yield_spread_ke_et.pdf` | Kenya minus Ethiopia yield spread per tenor |
| `local_real_yield_tenor_comparison.pdf` | Inflation-adjusted real yields, 3-panel by tenor |
| `real_yield_fx_tenor_comparison.pdf` | FX-adjusted real yields, 3-panel by tenor |
| `annualized_inflation_ke_et.pdf` | Annualized inflation with 3-month moving average |
| `annualized_fx_rate_ke_et.pdf` | Annualized FX depreciation with 3-month moving average |
| `summary.csv` | Descriptive statistics summary table |

---

## Canonical T-Bill Schema

All parsed T-Bill data (both countries) follows this column structure:

| Column | Description |
|--------|-------------|
| `Tenor` | Bill maturity (91 DAYS, 182 DAYS, 364 DAYS) |
| `Maturity Date` | Date the bill matures |
| `Amount Offered (Millions)` | Total amount offered at auction |
| `Bids Received (Millions)` | Total competitive + non-competitive bids |
| `Total Amount Accepted (Millions)` | Amount actually accepted by the central bank |
| `Weighted Average Yield (Annual in %)` | Yield weighted by accepted amount |
| `Weighted Average Price (Per 100)` | Price weighted by accepted amount |
| `Issue Number` | Auction issue identifier |
| `Issue Date` | Date the bill was issued |
| `Country` | Kenya or Ethiopia |
| `Currency` | Kshs or ETB |

---

## Dependencies

Key libraries (full list in `requirements.txt`):

- `requests` — HTTP scraping
- `beautifulsoup4` + `lxml` — HTML parsing
- `pdfplumber` + `pypdf` — PDF text and table extraction
- `pandas` — Data manipulation and CSV I/O
- `matplotlib` — Chart generation

---

## Notes on AI Assistance

An AI assistant was used to help with some pandas DataFrame manipulation and debugging. The project structure, scraping logic, and parsing code are the author's own.
