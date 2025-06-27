# plot_sector_correlation.py
"""
Read `sector_etf_correlation.csv`, plot a blue-white-red heatmap labeled by industry,
and save as `sector_etf_correlation.png` (overwriting any previous).
"""
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── Mapping ────────────────────────────────────────────────────────────────────
INDUSTRY_LABELS = {
    "XLK":  "Technology",
    "XLF":  "Financials",
    "XLE":  "Energy",
    "XLI":  "Industrials",
    "XLP":  "Consumer Staples",
    "XLU":  "Utilities",
    "XLV":  "Health Care",
    "XLY":  "Consumer Discretionary",
    "XLB":  "Materials",
    "XLRE": "Real Estate",
    "XLC":  "Communication Services",
}
INPUT_CSV = "sector_etf_correlation.csv"
OUTPUT_PNG = "sector_etf_correlation.png"
# ───────────────────────────────────────────────────────────────────────────────

# Remove old PNG
if os.path.exists(OUTPUT_PNG):
    try:
        os.remove(OUTPUT_PNG)
    except OSError:
        pass

# Load
if not os.path.exists(INPUT_CSV):
    print(f"❌ {INPUT_CSV} not found", file=sys.stderr)
    sys.exit(1)

corr = pd.read_csv(INPUT_CSV, index_col=0)
# Validate square
if corr.shape[0] != corr.shape[1]:
    print(f"❌ {INPUT_CSV} is not square: {corr.shape}", file=sys.stderr)
    sys.exit(1)

tickers = corr.columns.tolist()
labels = [INDUSTRY_LABELS.get(t, t) for t in tickers]

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr.values, cmap='bwr', vmin=-1, vmax=1)
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_yticklabels(labels)
for i in range(len(labels)):
    for j in range(len(labels)):
        ax.text(j, i, f"{corr.iat[i,j]:.2f}", ha='center', va='center', fontsize='small')
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Correlation', rotation=270, labelpad=15)
plt.title('Daily % Correlation')
plt.tight_layout()
fig.savefig(OUTPUT_PNG, format='png')
print(f"✅ Heatmap saved as {OUTPUT_PNG}")
