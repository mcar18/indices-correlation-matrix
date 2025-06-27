import yfinance as yf
import pandas as pd

sectors = ['XLK','XLF','XLE','XLI','XLP','XLU','XLV','XLY','XLB','XLRE','XLK']
data = yf.download(sectors, period='1y', interval='1d')['Adj Close'].pct_change().dropna()

correlation_matrix = data.corr()
#print(correlation_matrix)