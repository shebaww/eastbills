import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from paths import data, results, MASTER_CSV, INF_MASTER_CSV, master_fx_csv
from . import analysis
import pandas as pd
import numpy as np


class Illustrate:
    def __init__(self):
        self.Calc = analysis.Calc()
        self.master_inflation = pd.read_csv(INF_MASTER_CSV)
        self.master_fx = pd.read_csv(master_fx_csv)
        self.df = pd.read_csv(MASTER_CSV)
        self.df["Issue Date"] = pd.to_datetime(self.df["Issue Date"], errors="coerce")
        self.df_compared = self.df.loc[self.df["Tenor"] != "28 DAYS"]
        self.df_compared.reset_index(drop=True, inplace=True)
        self.df_compared.sort_values("Issue Date", inplace=True)

        self.eth_tenor_91 = self.df_compared.loc[(self.df_compared["Tenor"] == "91 DAYS") & (self.df_compared["Country"] == "Ethiopia")]
        self.eth_tenor_182 = self.df_compared.loc[(self.df_compared["Tenor"] == "182 DAYS") & (self.df_compared["Country"] == "Ethiopia")]
        self.eth_tenor_364 = self.df_compared.loc[(self.df_compared["Tenor"] == "364 DAYS") & (self.df_compared["Country"] == "Ethiopia")]
        
        self.ksh_tenor_91 = self.df_compared.loc[(self.df_compared["Tenor"] == "91 DAYS") & (self.df_compared["Country"] == "Kenya")]
        self.ksh_tenor_182 = self.df_compared.loc[(self.df_compared["Tenor"] == "182 DAYS") & (self.df_compared["Country"] == "Kenya")]
        self.ksh_tenor_364 = self.df_compared.loc[(self.df_compared["Tenor"] == "364 DAYS") & (self.df_compared["Country"] == "Kenya")]

        
    
    def run(self):
        self.nominal_yield()
        self.yield_spread()
        self.local_real_yield()
        self.real_yield_fx()
        self.annualized_inflation()
        self.annualized_fx_rate()

    def nominal_yield(self):
        tenor_colors = {"91 DAYS": "#1f77b4", "182 DAYS": "#ff7f0e", "364 DAYS": "#2ca02c"}
        tenor_ls = {"91 DAYS": "-", "182 DAYS": "--", "364 DAYS": "-."}
        tenors = ["91 DAYS", "182 DAYS", "364 DAYS"]

        fig, axes = plt.subplots(
            2, 1, figsize=(13, 8), sharex=True, sharey=True,
            gridspec_kw={"hspace": 0.12},
        )

        panels = [
            (axes[0], "Ethiopia",
             {"91 DAYS":  self.eth_tenor_91,
              "182 DAYS": self.eth_tenor_182,
              "364 DAYS": self.eth_tenor_364}),
            (axes[1], "Kenya",
             {"91 DAYS":  self.ksh_tenor_91,
              "182 DAYS": self.ksh_tenor_182,
              "364 DAYS": self.ksh_tenor_364}),
        ]

        for ax, country, by_tenor in panels:
            for tenor in tenors:
                d = by_tenor[tenor].copy()
                d["Issue Date"] = pd.to_datetime(d["Issue Date"], errors="coerce")
                d = d.dropna(subset=["Issue Date"]).sort_values("Issue Date")
                ax.plot(
                    d["Issue Date"],
                    d["Weighted Average Yield (Annual in %)"],
                    color=tenor_colors[tenor],
                    linewidth=1.6,
                    label=tenor.replace(" DAYS", "d"),
                    ls = tenor_ls[tenor]
                )

            ax.set_ylabel("Yield (%)", fontsize=10)
            ax.set_xlabel("")
            ax.set_xlabel("Issue Month", fontsize=10)
            ax.grid(True, alpha=0.25, linewidth=0.6)
            ax.set_axisbelow(True)
            ax.legend(
                title=country, loc="upper left", frameon=False,
                fontsize=9, title_fontsize=10,
            )
            ax.spines[["top", "right"]].set_visible(False)

        axes[1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.setp(axes[1].get_xticklabels(), rotation=0, ha="center")

        # tighten x to the data
        all_dates = pd.concat([
            pd.to_datetime(df["Issue Date"], errors="coerce")
            for panel in [self.eth_tenor_91, self.eth_tenor_182, self.eth_tenor_364,
                          self.ksh_tenor_91, self.ksh_tenor_182, self.ksh_tenor_364]
            for df in [panel]
        ]).dropna()
        axes[1].set_xlim(all_dates.min(), all_dates.max())

        plt.savefig(results / 'time-series-yield-curve.pdf', format="pdf", bbox_inches="tight")
        print("Saved to:", results / "time-series-yield-curve.pdf")


    
    def yield_spread(self):
        spread_91, spread_182, spread_364 = self.Calc.yield_spread()

        # ---- figure setup ----
        fig, ax = plt.subplots(figsize=(11, 6), dpi=150)

        colors = {
            "91d":  "#1f77b4",   # blue
            "182d": "#ff7f0e",   # orange
            "364d": "#2ca02c",   # green
        }

        for label, s, key, lsa in [
            ("91-day",  spread_91,  "91d", "-"),
            ("182-day", spread_182, "182d", "--"),
            ("364-day", spread_364, "364d", "-."),
        ]:
            ax.plot(
                s.index,
                s.to_numpy(),
                color=colors[key],
                linewidth=1.8,
                marker="o",
                markersize=3.5,
                markeredgewidth=0,
                label=f"{label} tenor",
                ls=lsa
            )

        # ---- reference line: zero spread ----
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.7)

        # ---- axes ----
        ax.set_xlabel("Issue month", fontsize=11)
        ax.set_ylabel("Yield Spread (Percentage Points)", fontsize=11)

        # ---- x-axis: quarterly ticks, no rotation, no phantom dates ----
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.tick_params(axis="x", which="major", length=5)
        ax.tick_params(axis="x", which="minor", length=2, color="#bbbbbb")

        # ---- y-axis: tighter, cleaner ----
        ax.yaxis.set_major_locator(MultipleLocator(2.5))
        ax.tick_params(axis="y", labelsize=10)

        # ---- grid & spines ----
        ax.grid(True, which="major", axis="y", alpha=0.25, linewidth=0.6)
        ax.grid(True, which="major", axis="x", alpha=0.15, linewidth=0.6)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#888888")
        ax.spines["bottom"].set_color("#888888")

        # ---- legend ----
        leg = ax.legend(
            loc="lower right",
            frameon=True,
            framealpha=0.95,
            edgecolor="#dddddd",
            fontsize=10,
            title="Spread by tenor",
            title_fontsize=10,
        )
        leg.get_frame().set_linewidth(0.6)

        fig.tight_layout(rect=[0, 0.02, 1, 1])

        # ---- save as vector PDF ----
        fig.savefig( results / "yield_spread_ke_et.pdf", bbox_inches="tight")
        print("Saved to:", results / "yield_spread_ke_et.pdf")
        plt.close(fig)     # don't call plt.show() after saving in a script
     
    def local_real_yield(self):
        # Unpack all six local real yield series
        (
            r_l_91_ksh, r_l_182_ksh, r_l_364_ksh, 
            r_l_91_eth, r_l_182_eth, r_l_364_eth
        ) = self.Calc.local_real_yield()

        # ---- Figure setup: 3-panel stack for direct tenor comparison ----
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 10), dpi=150, sharex=True)

        # Color & style definition: Keep country colors consistent across panels
        country_styles = {
            "KSH": {"color": "#1f77b4", "ls": "-",  "lw": 1.8, "marker": "o", "ms": 3.0, "name": "Kenya (KSH)"},
            "ETH": {"color": "#d62728", "ls": "--", "lw": 1.8, "marker": "s", "ms": 3.0, "name": "Ethiopia (ETH)"},
        }

        dates = pd.to_datetime(self.master_inflation["date"])

        # Mapping of Tenor Panels -> (Ax, KSH Series, ETH Series, Title/Label)
        tenor_panels = [
            (ax1, r_l_91_ksh,  r_l_91_eth,  "91-Day Tenor"),
            (ax2, r_l_182_ksh, r_l_182_eth, "182-Day Tenor"),
            (ax3, r_l_364_ksh, r_l_364_eth, "364-Day Tenor"),
        ]

        for ax, ksh_series, eth_series, tenor_title in tenor_panels:
            # Plot Kenya (KSH)
            ax.plot(
                dates,
                ksh_series,
                color=country_styles["KSH"]["color"],
                linestyle=country_styles["KSH"]["ls"],
                linewidth=country_styles["KSH"]["lw"],
                marker=country_styles["KSH"]["marker"],
                markersize=country_styles["KSH"]["ms"],
                markeredgewidth=0,
                label=country_styles["KSH"]["name"]
            )

            # Plot Ethiopia (ETH)
            ax.plot(
                dates,
                eth_series,
                color=country_styles["ETH"]["color"],
                linestyle=country_styles["ETH"]["ls"],
                linewidth=country_styles["ETH"]["lw"],
                marker=country_styles["ETH"]["marker"],
                markersize=country_styles["ETH"]["ms"],
                markeredgewidth=0,
                label=country_styles["ETH"]["name"]
            )

            # Reference zero line for real yields (Real Return Threshold)
            ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.7)

            # Axis labeling & titles
            ax.set_ylabel("Real Yield (%)", fontsize=10)
            
            # In-axes panel title annotation (cleaner than default subplot titles)
            ax.text(
                0.015, 0.90, tenor_title,
                transform=ax.transAxes,
                fontsize=10.5,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9)
            )

            # Axis tick formatting
            ax.yaxis.set_major_locator(MultipleLocator(2.5))
            ax.tick_params(axis="y", labelsize=9.5)

            # Grids & Spines
            ax.grid(True, which="major", axis="y", alpha=0.25, linewidth=0.6)
            ax.grid(True, which="major", axis="x", alpha=0.15, linewidth=0.6)
            ax.set_axisbelow(True)

            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#888888")
            ax.spines["bottom"].set_color("#888888")

            # Clean Legend
            leg = ax.legend(
                loc="lower right",
                frameon=True,
                framealpha=0.95,
                edgecolor="#dddddd",
                fontsize=9.5,
                ncol=2
            )
            leg.get_frame().set_linewidth(0.6)

        # ---- X-axis Date Formatting (Bottom Plot Only) ----
        ax3.set_xlabel("Issue Month", fontsize=11)
        ax3.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax3.xaxis.set_minor_locator(mdates.MonthLocator())
        ax3.tick_params(axis="x", which="major", length=5)
        ax3.tick_params(axis="x", which="minor", length=2, color="#bbbbbb")

        # Tight layout adjustments for figure saving
        fig.tight_layout(rect=[0, 0.02, 1, 1])

        # Save vector PDF for inclusion in paper / thesis
        output_path = results / "local_real_yield_tenor_comparison.pdf"
        fig.savefig(output_path, bbox_inches="tight")
        print("Saved to:", output_path)
        plt.close(fig)

    def real_yield_fx(self):
        # Unpack FX-adjusted real yield series
        (
            r_fx_91_ksh, r_fx_182_ksh, r_fx_364_ksh, 
            r_fx_91_eth, r_fx_182_eth, r_fx_364_eth
        ) = self.Calc.real_yield_fx()

        # Explicitly cast dates to datetime to avoid Unix Epoch error
        dates = pd.to_datetime(self.master_fx["date"])

        country_styles = {
            "KSH": {"color": "#1f77b4", "ls": "-",  "lw": 1.8, "marker": "o", "ms": 3.0, "name": "Kenya (KSH)"},
            "ETH": {"color": "#d62728", "ls": "--", "lw": 1.8, "marker": "s", "ms": 3.0, "name": "Ethiopia (ETH)"},
        }

        tenor_panels = [
            ("91-Day Tenor (FX-Adjusted)", r_fx_91_ksh, r_fx_91_eth),
            ("182-Day Tenor (FX-Adjusted)", r_fx_182_ksh, r_fx_182_eth),
            ("364-Day Tenor (FX-Adjusted)", r_fx_364_ksh, r_fx_364_eth),
        ]

        # ---- Figure setup: 3-panel stack ----
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 10), dpi=150, sharex=True)
        axes = [ax1, ax2, ax3]

        for ax, (tenor_title, ksh_series, eth_series) in zip(axes, tenor_panels):
            # Plot Kenya (KSH)
            ax.plot(
                dates, ksh_series,
                color=country_styles["KSH"]["color"],
                linestyle=country_styles["KSH"]["ls"],
                linewidth=country_styles["KSH"]["lw"],
                marker=country_styles["KSH"]["marker"],
                markersize=country_styles["KSH"]["ms"],
                markeredgewidth=0,
                label=country_styles["KSH"]["name"]
            )

            # Plot Ethiopia (ETH)
            ax.plot(
                dates, eth_series,
                color=country_styles["ETH"]["color"],
                linestyle=country_styles["ETH"]["ls"],
                linewidth=country_styles["ETH"]["lw"],
                marker=country_styles["ETH"]["marker"],
                markersize=country_styles["ETH"]["ms"],
                markeredgewidth=0,
                label=country_styles["ETH"]["name"]
            )

            # Reference zero line
            ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.7)

            # Truncate Y-axis to standard economic bounds (hiding the -417 extreme spike cleanly)
            ax.set_ylim(-30, 20)

            # Axis labels & panel title badge
            ax.set_ylabel("FX Real Yield (%)", fontsize=10)
            ax.text(
                0.015, 0.88, tenor_title,
                transform=ax.transAxes,
                fontsize=10.5,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9)
            )

            ax.yaxis.set_major_locator(MultipleLocator(10.0))
            ax.tick_params(axis="y", labelsize=9.5)

            # Grids & Spines
            ax.grid(True, which="major", axis="y", alpha=0.25, linewidth=0.6)
            ax.grid(True, which="major", axis="x", alpha=0.15, linewidth=0.6)
            ax.set_axisbelow(True)

            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#888888")
            ax.spines["bottom"].set_color("#888888")

            leg = ax.legend(
                loc="upper right",
                frameon=True,
                framealpha=0.95,
                edgecolor="#dddddd",
                fontsize=9.5,
                ncol=2
            )
            leg.get_frame().set_linewidth(0.6)

        # ---- Off-Chart Annotation for the August 2024 Crisis Spike (-417%) ----
        # Applied to the top panel (or all panels if needed)
        crash_date = pd.to_datetime("2024-08-01") # Adjust if your exact date differs slightly
        ax1.annotate(
            'Ethiopia Aug 2024:\n-417%', 
            xy=(crash_date, -30), # Pointing to the bottom edge of the plot
            xytext=(crash_date + pd.Timedelta(days=20), -18), # Text placement inside the visible region
            arrowprops=dict(facecolor='#d62728', edgecolor='#d62728', arrowstyle='->', lw=1.2),
            fontsize=9.5, color='#d62728', fontweight='bold'
        )

        # ---- X-axis Date Formatting (Bottom Plot Only) ----
        ax3.set_xlabel("Issue Month", fontsize=11)
        ax3.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax3.xaxis.set_minor_locator(mdates.MonthLocator())
        ax3.tick_params(axis="x", which="major", length=5)
        ax3.tick_params(axis="x", which="minor", length=2, color="#bbbbbb")

        fig.tight_layout(rect=[0, 0.02, 1, 1])

        # ---- Save as vector PDF ----
        output_path = results / "real_yield_fx_tenor_comparison.pdf"
        fig.savefig(output_path, bbox_inches="tight")
        print("Saved to:", output_path)
        plt.close(fig)

    def annualized_inflation(self):
        ann_inf = self.Calc._annualizing_inflation(self.master_inflation)

        # Explicitly cast dates to datetime to prevent Unix Epoch error
        dates = pd.to_datetime(self.master_inflation["date"])

        # ---- Figure setup ----
        fig, ax = plt.subplots(figsize=(11, 6), dpi=150)

        # Country styling taxonomy
        styles = {
            "Kenya": {"color": "#1f77b4", "ls": "-", "lw": 1.8, "marker": "o", "ms": 3.0, "label": "Kenya (3MA)"},
            "Ethiopia": {"color": "#d62728", "ls": "--", "lw": 1.8, "marker": "s", "ms": 3.0, "label": "Ethiopia (3MA)"},
        }

        # Plot Kenya & Ethiopia Annualized Inflation 3MA
        ax.plot(dates, ann_inf["Kenya 3MA"], color=styles["Kenya"]["color"], ls=styles["Kenya"]["ls"],
                lw=styles["Kenya"]["lw"], marker=styles["Kenya"]["marker"], ms=styles["Kenya"]["ms"], markeredgewidth=0, label=styles["Kenya"]["label"])

        ax.plot(dates, ann_inf["ethiopia 3MA"], color=styles["Ethiopia"]["color"], ls=styles["Ethiopia"]["ls"],
                lw=styles["Ethiopia"]["lw"], marker=styles["Ethiopia"]["marker"], ms=styles["Ethiopia"]["ms"], markeredgewidth=0, label=styles["Ethiopia"]["label"])

        # ---- Reference zero line ----
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.7)

        # ---- Truncate Y-axis to standard economic bounds (preventing extreme inflation outlier squishing) ----
        ax.set_ylim(-10, 50) # Adjust upper/lower bounds if your max inflation is higher/lower

        # ---- Axes Labels & Formatting ----
        ax.set_xlabel("Observation Month", fontsize=11)
        ax.set_ylabel("Annualized Inflation (%)", fontsize=11)

        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.tick_params(axis="x", which="major", length=5)
        ax.tick_params(axis="x", which="minor", length=2, color="#bbbbbb")

        ax.yaxis.set_major_locator(MultipleLocator(10))
        ax.tick_params(axis="y", labelsize=10)

        # ---- Grids & Spines ----
        ax.grid(True, which="major", axis="y", alpha=0.25, linewidth=0.6)
        ax.grid(True, which="major", axis="x", alpha=0.15, linewidth=0.6)
        ax.set_axisbelow(True)

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#888888")
        ax.spines["bottom"].set_color("#888888")

        # ---- Legend ----
        leg = ax.legend(
            loc="upper right",
            frameon=True,
            framealpha=0.95,
            edgecolor="#dddddd",
            fontsize=10,
            title="Annualized Inflation (3MA)",
            title_fontsize=10,
        )
        leg.get_frame().set_linewidth(0.6)

        fig.tight_layout(rect=[0, 0.02, 1, 1])

        # ---- Save as vector PDF ----
        output_path = results / "annualized_inflation_ke_et.pdf"
        fig.savefig(output_path, bbox_inches="tight")
        print("Saved to:", output_path)
        plt.close(fig)

    def annualized_fx_rate(self):
        ann_fx = self.Calc._annualizing_fx_rates(self.master_fx)
        
        # Explicitly cast dates to datetime to prevent Unix Epoch error
        # (Using master_fx date column as intended for fx rates)
        dates = pd.to_datetime(self.master_fx["date"])

        # ---- Figure setup ----
        fig, ax = plt.subplots(figsize=(11, 6), dpi=150)

        styles = {
            "Kenya": {"color": "#1f77b4", "ls": "-", "lw": 1.8, "marker": "o", "ms": 3.0, "label": "Kenya FX (3MA)"},
            "Ethiopia": {"color": "#d62728", "ls": "--", "lw": 1.8, "marker": "s", "ms": 3.0, "label": "Ethiopia FX (3MA)"},
        }

        # Plot Kenya & Ethiopia Annualized FX Rates 3MA
        ax.plot(dates, ann_fx["Kenya 3MA"], color=styles["Kenya"]["color"], ls=styles["Kenya"]["ls"], 
                lw=styles["Kenya"]["lw"], marker=styles["Kenya"]["marker"], ms=styles["Kenya"]["ms"], markeredgewidth=0, label=styles["Kenya"]["label"])
        
        ax.plot(dates, ann_fx["Ethiopia 3MA"], color=styles["Ethiopia"]["color"], ls=styles["Ethiopia"]["ls"], 
                lw=styles["Ethiopia"]["lw"], marker=styles["Ethiopia"]["marker"], ms=styles["Ethiopia"]["ms"], markeredgewidth=0, label=styles["Ethiopia"]["label"])

        # ---- Reference zero line ----
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--", alpha=0.7)

        # ---- Truncate Y-axis to remove extreme FX depreciation tail-outliers ----
        ax.set_ylim(-20, 100) # Prevents massive FX structural devaluation spikes from breaking scale layout

        # ---- Axes Labels & Formatting ----
        ax.set_xlabel("Observation Month", fontsize=11)
        ax.set_ylabel("Annualized FX Depreciation Rate (%)", fontsize=11)

        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.tick_params(axis="x", which="major", length=5)
        ax.tick_params(axis="x", which="minor", length=2, color="#bbbbbb")

        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.tick_params(axis="y", labelsize=10)

        # ---- Grids & Spines ----
        ax.grid(True, which="major", axis="y", alpha=0.25, linewidth=0.6)
        ax.grid(True, which="major", axis="x", alpha=0.15, linewidth=0.6)
        ax.set_axisbelow(True)

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#888888")
        ax.spines["bottom"].set_color("#888888")

        # ---- Legend ----
        leg = ax.legend(
            loc="upper right",
            frameon=True,
            framealpha=0.95,
            edgecolor="#dddddd",
            fontsize=10,
            title="Annualized FX Rate (3MA)",
            title_fontsize=10,
        )
        leg.get_frame().set_linewidth(0.6)

        fig.tight_layout(rect=[0, 0.02, 1, 1])

        # ---- Save as vector PDF ----
        output_path = results / "annualized_fx_rate_ke_et.pdf"
        fig.savefig(output_path, bbox_inches="tight")
        print("Saved to:", output_path)
        plt.close(fig)



