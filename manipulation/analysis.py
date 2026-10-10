import pandas as pd
import numpy as np
from paths import MASTER_CSV, INF_MASTER_CSV, master_fx_csv, ETH_CSV, SUM_CSV, KSH_CSV

class Calc:
    def __init__(self):
        self.df = pd.read_csv(MASTER_CSV)
        self.master_inflation = pd.read_csv(INF_MASTER_CSV)
        self.master_fx = pd.read_csv(master_fx_csv)
        self.df["Issue Date"] = pd.to_datetime(self.df["Issue Date"], errors="coerce")
        self.df_compared = self.df.loc[self.df["Tenor"] != "28 DAYS"]
        self.df_compared.sort_values("Issue Date", inplace=True)
        self.df_compared.reset_index(drop=True, inplace=True)

        self.eth_tenor_91 = self.df_compared.loc[(self.df_compared["Tenor"] == "91 DAYS") & (self.df_compared["Country"] == "Ethiopia")]
        self.eth_tenor_182 = self.df_compared.loc[(self.df_compared["Tenor"] == "182 DAYS") & (self.df_compared["Country"] == "Ethiopia")]
        self.eth_tenor_364 = self.df_compared.loc[(self.df_compared["Tenor"] == "364 DAYS") & (self.df_compared["Country"] == "Ethiopia")]
        
        self.ksh_tenor_91 = self.df_compared.loc[(self.df_compared["Tenor"] == "91 DAYS") & (self.df_compared["Country"] == "Kenya")]
        self.ksh_tenor_182 = self.df_compared.loc[(self.df_compared["Tenor"] == "182 DAYS") & (self.df_compared["Country"] == "Kenya")]
        self.ksh_tenor_364 = self.df_compared.loc[(self.df_compared["Tenor"] == "364 DAYS") & (self.df_compared["Country"] == "Kenya")]

    
    def _monthly_yield(self):
        
            # Kenya - Ethiopia
        """ Ethiopia Monthly Yield"""
        eth_tenor_91 = self.eth_tenor_91[["Weighted Average Yield (Annual in %)", "Issue Date", "Total Amount Accepted (Millions)"]].copy()
        eth_tenor_91 = eth_tenor_91.dropna(subset=["Issue Date", "Weighted Average Yield (Annual in %)"])
        eth_tenor_91 = eth_tenor_91.set_index("Issue Date").sort_index()


        eth_tenor_182 = self.eth_tenor_182[["Weighted Average Yield (Annual in %)", "Issue Date", "Total Amount Accepted (Millions)"]].copy()
        eth_tenor_182 = eth_tenor_182.dropna(subset=["Issue Date", "Weighted Average Yield (Annual in %)"])
        eth_tenor_182 = eth_tenor_182.set_index("Issue Date").sort_index()


        eth_tenor_364 = self.eth_tenor_364[["Weighted Average Yield (Annual in %)", "Issue Date", "Total Amount Accepted (Millions)"]].copy()
        eth_tenor_364 = eth_tenor_364.dropna(subset=["Issue Date", "Weighted Average Yield (Annual in %)"])
        eth_tenor_364 = eth_tenor_364.set_index("Issue Date").sort_index()

        

        eth_y_91 = eth_tenor_91["Weighted Average Yield (Annual in %)"]
        eth_y_182 = eth_tenor_182["Weighted Average Yield (Annual in %)"]
        eth_y_364 = eth_tenor_364["Weighted Average Yield (Annual in %)"]
        
        
        eth_w_91 = eth_tenor_91["Total Amount Accepted (Millions)"]
        eth_w_182 = eth_tenor_182["Total Amount Accepted (Millions)"]
        eth_w_364 = eth_tenor_364["Total Amount Accepted (Millions)"]

        eth_monthly_91 = (
                            (eth_y_91 * eth_w_91).resample("ME").sum()
                               / 
                            eth_w_91.resample("ME").sum()
        )

        eth_monthly_182 = (
                            (eth_y_182 * eth_w_182).resample("ME").sum()
                               /
                            eth_w_182.resample("ME").sum()
        )

        eth_monthly_364 = (
                            (eth_y_364 * eth_w_364).resample("ME").sum()
                               /
                            eth_w_364.resample("ME").sum()
        )



        """ Kenya Monthly Yield"""
        ksh_tenor_91 = self.ksh_tenor_91[["Weighted Average Yield (Annual in %)", "Issue Date", "Total Amount Accepted (Millions)"]].copy()
        ksh_tenor_91 = ksh_tenor_91.dropna(subset=["Issue Date", "Weighted Average Yield (Annual in %)"])
        ksh_tenor_91 = ksh_tenor_91.set_index("Issue Date").sort_index()


        ksh_tenor_182 = self.ksh_tenor_182[["Weighted Average Yield (Annual in %)", "Issue Date", "Total Amount Accepted (Millions)"]].copy()
        ksh_tenor_182 = ksh_tenor_182.dropna(subset=["Issue Date", "Weighted Average Yield (Annual in %)"])
        ksh_tenor_182 = ksh_tenor_182.set_index("Issue Date").sort_index()


        ksh_tenor_364 = self.ksh_tenor_364[["Weighted Average Yield (Annual in %)", "Issue Date", "Total Amount Accepted (Millions)"]].copy()
        ksh_tenor_364 = ksh_tenor_364.dropna(subset=["Issue Date", "Weighted Average Yield (Annual in %)"])
        ksh_tenor_364 = ksh_tenor_364.set_index("Issue Date").sort_index()



        ksh_y_91 = ksh_tenor_91["Weighted Average Yield (Annual in %)"]
        ksh_y_182 = ksh_tenor_182["Weighted Average Yield (Annual in %)"]
        ksh_y_364 = ksh_tenor_364["Weighted Average Yield (Annual in %)"]


        ksh_w_91 = ksh_tenor_91["Total Amount Accepted (Millions)"]
        ksh_w_182 = ksh_tenor_182["Total Amount Accepted (Millions)"]
        ksh_w_364 = ksh_tenor_364["Total Amount Accepted (Millions)"]

        ksh_monthly_91 = (
                            (ksh_y_91 * ksh_w_91).resample("ME").sum()
                               /
                            ksh_w_91.resample("ME").sum()
        )

        ksh_monthly_182 = (
                            (ksh_y_182 * ksh_w_182).resample("ME").sum()
                               /
                            ksh_w_182.resample("ME").sum()
        )

        ksh_monthly_364 = (
                            (ksh_y_364 * ksh_w_364).resample("ME").sum()
                               /
                            ksh_w_364.resample("ME").sum()
        )
        
        return  ksh_monthly_91, ksh_monthly_182, ksh_monthly_364, eth_monthly_91, eth_monthly_182, eth_monthly_364


    def yield_spread(self):
        ksh_monthly_91, ksh_monthly_182, ksh_monthly_364, eth_monthly_91, eth_monthly_182, eth_monthly_364 = self._monthly_yield()
        spread_91 = ksh_monthly_91 - eth_monthly_91
        spread_182 = ksh_monthly_182 - eth_monthly_182
        spread_364 = ksh_monthly_364 - eth_monthly_364

        return spread_91, spread_182, spread_364
   
    
    def local_real_yield(self):
# This is not your usual series it is a df
        ksh_monthly_91, ksh_monthly_182, ksh_monthly_364, eth_monthly_91, eth_monthly_182, eth_monthly_364 = self._turn_series_to_df(self._monthly_yield())

        ann_inf = self._annualizing_inflation(self.master_inflation)
            
        r_l_91_ksh = ksh_monthly_91["Yield"] - ann_inf["Kenya 3MA"]
        r_l_182_ksh = ksh_monthly_182["Yield"] - ann_inf["Kenya 3MA"]
        r_l_364_ksh = ksh_monthly_364["Yield"] - ann_inf["Kenya 3MA"]

        r_l_91_eth = eth_monthly_91["Yield"] - ann_inf["ethiopia 3MA"]
        r_l_182_eth = eth_monthly_182["Yield"] - ann_inf["ethiopia 3MA"]
        r_l_364_eth = eth_monthly_364["Yield"] - ann_inf["ethiopia 3MA"]

        return r_l_91_ksh, r_l_182_ksh, r_l_364_ksh, r_l_91_eth, r_l_182_eth, r_l_364_eth


      
    def real_yield_fx(self):
        r_l_91_ksh, r_l_182_ksh, r_l_364_ksh, r_l_91_eth, r_l_182_eth, r_l_364_eth = self.local_real_yield()
        ann_fx = self._annualizing_fx_rates(self.master_fx)

        r_fx_91_ksh = r_l_91_ksh - ann_fx["Kenya 3MA"]
        r_fx_182_ksh = r_l_182_ksh - ann_fx["Kenya 3MA"]
        r_fx_364_ksh = r_l_364_ksh - ann_fx["Kenya 3MA"]

        r_fx_91_eth = r_l_91_eth - ann_fx["Ethiopia 3MA"]
        r_fx_182_eth = r_l_182_eth - ann_fx["Ethiopia 3MA"]
        r_fx_364_eth = r_l_364_eth - ann_fx["Ethiopia 3MA"]

        return r_fx_91_ksh, r_fx_182_ksh, r_fx_364_ksh, r_fx_91_eth, r_fx_182_eth, r_fx_364_eth


    def _turn_series_to_df(self, monthly_series):
        """ Turns Series into a Data Frame, Turns index into "date" column assigns proper yield column, Floors all "date" to 01 """
        df_list = []
        for series in monthly_series:
          series = series.reset_index()
          series.columns=(["date", "Yield"])
          series["date"] = series["date"].dt.to_period("M").dt.to_timestamp()
# Filter to study specific date
          series = series[~(series["date"] < "2024-08-01") & ~(series["date"] > "2026-05-01")]
          series.reset_index(inplace=True, drop=True)
          df_list.append(series)

        return df_list
    
        
    def _annualizing_fx_rates(self, df: pd.DataFrame) -> pd.DataFrame:
            ann_df = df.copy()

            # Use raw df["Ethiopia Rate"] to avoid reading overwritten values!
            ann_df["Ethiopia Annualized"] = ((df["Ethiopia Rate"] / df["Ethiopia Rate"].shift(1))**12 - 1) * 100
            ann_df["Kenya Annualized"] = ((df["Kenya Rate"] / df["Kenya Rate"].shift(1))**12 - 1) * 100

            # Calculate 3MA on the annualized columns
            ann_df["Ethiopia 3MA"] = ann_df["Ethiopia Annualized"].rolling(window=3).mean()
            ann_df["Kenya 3MA"] = ann_df["Kenya Annualized"].rolling(window=3).mean()

            return ann_df
      
    
    def _annualizing_inflation(self, df: pd.DataFrame) -> pd.DataFrame:
        ann_df = df.copy()
        ann_df["ethiopia"] = ann_df["ethiopia"] / 100
        ann_df["Kenya"] = ann_df["Kenya"] / 100
        ann_df["ethiopia"] = ((1 + ann_df["ethiopia"])**12 - 1) * 100
        ann_df["Kenya"] = ((1 + ann_df["Kenya"])**12 - 1) * 100
        ann_df["ethiopia 3MA"] = ann_df["ethiopia"].rolling(window=3).mean()
        ann_df["Kenya 3MA"] = ann_df["Kenya"].rolling(window=3).mean()
        return ann_df



class Summary:
    def __init__(self):
        # Corrected file assignments
        self.eth_df = pd.read_csv(ETH_CSV)
        self.ksh_df = pd.read_csv(KSH_CSV)
         
    def run(self):
        # 1. Generate description statistics for each
        eth_summary = self.eth_df.describe()
        ksh_summary = self.ksh_df.describe()
        
        # 2. Clean up column names for academic presentation
        rename_dict = {
            'Amount Offered (Millions)': 'Amount Offered',
            'Bids Received (Millions)': 'Bids Received',
            'Total Amount Accepted (Millions)': 'Accepted Amount',
            'Weighted Average Yield (Annual in %)': 'Yield (%)',
            'Weighted Average Price (Per 100)': 'Price (Per 100)'
        }
        eth_summary = eth_summary.rename(columns=rename_dict)
        ksh_summary = ksh_summary.rename(columns=rename_dict)
        
        # 3. Combine them into a single multi-index DataFrame (Country, Statistic)
        combined_summary = pd.concat(
            {'Ethiopia': eth_summary, 'Kenya': ksh_summary},
            names=['Country', 'Statistic']
        )
        
        # 4. Save to a single CSV file
        print(f"Writing combined treasury bill summary table to: {SUM_CSV}")
        combined_summary.to_csv(SUM_CSV)
        print(combined_summary)

