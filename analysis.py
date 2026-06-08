"""
Trader Performance vs Market Sentiment — Hyperliquid x Fear/Greed Index
Author: Akshay
Generates all figures used in the analysis and prints the headline statistics.
"""
import pandas as pd, numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    "figure.dpi": 130, "font.size": 11, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25,
    "font.family": "DejaVu Sans",
})
FEAR, GREED, NEU = "#d1495b", "#2a9d8f", "#9aa0a6"
ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
CMAP = {"Extreme Fear": "#a4133c", "Fear": "#d1495b", "Neutral": "#9aa0a6",
        "Greed": "#52b788", "Extreme Greed": "#1b7a5e"}

# ---------- Load & merge ----------
def load():
    h = pd.read_csv("csv_files/historical_data.csv")
    h["dt"] = pd.to_datetime(h["Timestamp IST"], format="%d-%m-%Y %H:%M")
    h["date"] = h["dt"].dt.normalize()
    fg = pd.read_csv("csv_files/fear_greed_index.csv")
    fg["date"] = pd.to_datetime(fg["date"])
    m = h.merge(fg[["date", "classification", "value"]], on="date", how="left")
    m = m.dropna(subset=["classification"])
    m["fg"] = m["classification"].str.contains("Fear").map({True: "Fear", False: "Greed"})
    m.loc[m["classification"] == "Neutral", "fg"] = "Neutral"
    return m

m = load()
closed = m[m["Closed PnL"] != 0].copy()
closed["win"] = closed["Closed PnL"] > 0
print(f"Trades: {len(m):,} | matched to sentiment | closing trades: {len(closed):,}")

# ---------- Fig 1: win rate + avg PnL by regime ----------
g = closed.groupby("classification")
wr = g["win"].mean().reindex(ORDER)
pnl = g["Closed PnL"].mean().reindex(ORDER)
fig, ax1 = plt.subplots(figsize=(8.5, 4.8))
bars = ax1.bar(ORDER, wr.values, color=[CMAP[c] for c in ORDER], alpha=0.9)
ax1.set_ylabel("Win rate (closing trades)"); ax1.set_ylim(0, 1)
for b, v in zip(bars, wr.values):
    ax1.text(b.get_x()+b.get_width()/2, v+0.02, f"{v:.0%}", ha="center", fontsize=10, weight="bold")
ax2 = ax1.twinx()
ax2.plot(ORDER, pnl.values, "o-", color="#283618", lw=2, ms=7, label="Avg PnL / trade")
ax2.set_ylabel("Avg Closed PnL per trade ($)"); ax2.grid(False)
ax1.set_title("Win rate and average PnL by market sentiment", weight="bold")
ax2.legend(loc="upper center")
plt.tight_layout(); plt.savefig("outputs/01_winrate_pnl.png"); plt.close()

# ---------- Fig 2: contrarian positioning (the headline) ----------
opens = m[m["Direction"].isin(["Open Long", "Open Short"])]
mix = pd.crosstab(opens["classification"], opens["Direction"], normalize="index").reindex(ORDER)
fig, ax = plt.subplots(figsize=(8.5, 4.8))
ax.bar(ORDER, mix["Open Long"], color=GREED, label="Open Long", alpha=0.9)
ax.bar(ORDER, mix["Open Short"], bottom=mix["Open Long"], color=FEAR, label="Open Short", alpha=0.9)
ax.axhline(0.5, color="k", ls="--", lw=1, alpha=0.6)
for i, c in enumerate(ORDER):
    ax.text(i, mix["Open Long"][c]/2, f"{mix['Open Long'][c]:.0%}", ha="center", color="white", weight="bold")
ax.set_ylabel("Share of new positions opened"); ax.set_ylim(0, 1)
ax.set_title("Contrarian positioning: traders go LONG in Fear, SHORT in Greed", weight="bold")
ax.legend(loc="lower right")
plt.tight_layout(); plt.savefig("outputs/02_contrarian_positioning.png"); plt.close()

# ---------- Fig 3: risk-adjusted return + trade size ----------
ra = (g["Closed PnL"].mean() / g["Closed PnL"].std()).reindex(ORDER)
size = m.groupby("classification")["Size USD"].mean().reindex(ORDER)
fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 4.4))
a.bar(ORDER, ra.values, color=[CMAP[c] for c in ORDER], alpha=0.9)
a.set_title("Risk-adjusted return (mean/std of PnL)", weight="bold")
a.set_xticklabels(ORDER, rotation=25, ha="right")
b.bar(ORDER, size.values, color=[CMAP[c] for c in ORDER], alpha=0.9)
b.set_title("Average trade size (USD)", weight="bold")
b.set_xticklabels(ORDER, rotation=25, ha="right")
plt.tight_layout(); plt.savefig("outputs/03_riskadj_size.png"); plt.close()

# ---------- Stats ----------
print("\n--- Statistical tests ---")
o2 = opens[opens["classification"] != "Neutral"].copy()
o2["short"] = (o2["Direction"] == "Open Short").astype(int)
o2["fg"] = o2["classification"].str.contains("Fear").map({True: "Fear", False: "Greed"})
ct = pd.crosstab(o2["fg"], o2["short"])
chi2, p, _, _ = stats.chi2_contingency(ct)
print(f"Direction vs Fear/Greed (chi-square): chi2={chi2:.0f}, p={p:.2e}")
f = closed[closed["fg"] == "Fear"]["Closed PnL"]; gr = closed[closed["fg"] == "Greed"]["Closed PnL"]
u, pm = stats.mannwhitneyu(f, gr)
print(f"PnL Fear vs Greed (Mann-Whitney): p={pm:.3f}  (means ${f.mean():.0f} vs ${gr.mean():.0f})")
print("\nSaved 3 figures to outputs/")
