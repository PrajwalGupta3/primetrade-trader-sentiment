# Trader Performance vs Market Sentiment

Analysis of **211,218 Hyperliquid trades** (32 accounts, 246 coins, May 2023 – May 2025) against the daily **Bitcoin Fear & Greed Index**, exploring how trader behaviour and performance shift across sentiment regimes.

## TL;DR — Key Findings

1. **Positioning is contrarian and strongly sentiment-driven.** Traders open mostly **long during Fear** (69% long in Extreme Fear) and flip **net-short during Greed** (58% short). A chi-square test rejects independence decisively (χ² = 3051, p ≈ 0).
2. **Win rate peaks at sentiment extremes** — ~87% on Fear days and ~89% on Extreme Greed days — and dips in calm/neutral markets.
3. **There is *no* significant raw-PnL edge between Fear and Greed** (Mann-Whitney p = 0.53; mean $102 vs $106 per closing trade). This is the trap most analyses fall into — "Fear is more profitable" does **not** hold here.
4. **Best risk-adjusted regime is Extreme Greed** (mean/std of PnL = 0.12). **Extreme Fear is the most dangerous** — average loss −$257 vs average win +$173, the worst loss-to-win asymmetry of any regime.
5. **Actionable takeaway:** lean into the contrarian side the cohort already favours, but **cut position size in Extreme Fear**, where tail losses dominate and risk-adjusted returns collapse.

## Figures
| File | Shows |
|---|---|
| `outputs/01_winrate_pnl.png` | Win rate (bars) + avg PnL (line) per regime |
| `outputs/02_contrarian_positioning.png` | Long/short split of new positions per regime — the headline |
| `outputs/03_riskadj_size.png` | Risk-adjusted return and average trade size per regime |

## Repo Structure
```
ds_akshay/
├── notebook_1.ipynb   # full analysis (run top-to-bottom)
├── analysis.py        # same analysis as a script; regenerates outputs/
├── csv_files/         # the two source datasets
├── outputs/           # generated charts (PNG)
└── README.md
```

## How to Run
```bash
pip install pandas numpy scipy matplotlib
python analysis.py            # regenerates all figures + prints stats
# or open notebook_1.ipynb and Run All
```

## Method Notes
- Trader timestamps are IST (`dd-mm-yyyy hh:mm`), normalised to date and left-joined to the sentiment label. 211,218 / 211,224 rows match (6 fall outside the index range).
- The brief lists a `leverage` column; this export does not include one, so **`Size USD` is used as the position-size proxy**.
- `Closed PnL` is non-zero only on position-closing fills (104,402 rows), so all profitability metrics are computed on closing trades — opening fills carry no realised PnL.
