import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Map each sector-ETF ticker to its industry name
industry_labels = {
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

def plot_correlation_heatmap(csv_path: str):
    # 1) Load the correlation matrix
    corr = pd.read_csv(csv_path, index_col=0)

    # 2) Build industry-name labels
    tickers = corr.columns.tolist()
    labels = [industry_labels.get(t, t) for t in tickers]

    # 3) Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, cmap='bwr', vmin=-1, vmax=1)

    # 4) Set ticks
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)

    # 5) Annotate cells
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            ax.text(j, i, f"{corr.iat[i, j]:.2f}",
                    ha='center', va='center')

    # 6) Colorbar + title
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation", rotation=270, labelpad=15)
    plt.title("Sector ETF Daily-Return Correlation by Industry")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_correlation_heatmap("sector_etf_correlation_stooq_full.csv")