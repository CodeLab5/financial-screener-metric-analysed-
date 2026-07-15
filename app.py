import streamlit as st
import yfinance as yf
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Financial Screener", page_icon="📈", layout="wide")

st.title("📊 Financial Screener Dashboard")
st.write("Welcome to your interactive stock screener. Select options below to analyze data.")

# Add interactive sidebar inputs
st.sidebar.header("Screener Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL").upper()
period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "5y"])

# Fetch data dynamically
if ticker:
    try:
        # Download the stock data and tell yfinance to keep the columns flat
        data = yf.download(tickers=ticker, period=period, multi_level_index=False)
        
        # Display key metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"{ticker} Current Price", value=f"${data['Close'].iloc[-1]:.2f}")
        with col2:
            price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
            st.metric(label="Period Change", value=f"${price_change:.2f}", delta=f"{price_change:.2f}")

        # Interactive Chart
        st.subheader(f"{ticker} Price History")
        st.line_chart(data['Close'])

        # Structured Data Table
        st.subheader("Raw Financial Data")
        st.dataframe(data.tail(10))

    except Exception as e:
        st.error(f"Error fetching data for {ticker}. Please check the symbol and try again.")