import yfinance as yf
import pandas as pd
import streamlit as st

class DataManager:
    def __init__(self):
        self.cache = {}
        
    def get_stock_data(self, tickers, period="max"):
        """
        Fetch stock data from Yahoo Finance with caching
        """
        cache_key = f"{','.join(tickers)}_{period}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        with st.spinner(f'Downloading data for {len(tickers)} stocks...'):
            data = yf.download(
                tickers,
                period=period,
                progress=False
            )['Close']  # Changed from 'Adj Close' to 'Close'
            
            # Handle single ticker case
            if len(tickers) == 1:
                data = pd.DataFrame(data, columns=tickers)
            
            # Filter data from 1990 onwards if period is "max"
            if period == "max":
                data = data.loc["1990":]
                
            # Drop any rows with all NaN values
            data = data.dropna(how="all")
            
            self.cache[cache_key] = data
            
        return data 