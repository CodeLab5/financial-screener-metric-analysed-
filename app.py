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
        # Step 1: Initialize Ticker object to fetch correct local currency metadata
        ticker_info = yf.Ticker(ticker)
        
        # Pull currency from info dictionary; default to generic currency sign if unavailable
        raw_currency = ticker_info.info.get('currency', 'USD')
        currency_symbols = {'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 'CAD': 'CA$'}
        currency_symbol = currency_symbols.get(raw_currency, f"{raw_currency} ")

        # Step 2: Download the historical chart data flat
        data = yf.download(tickers=ticker, period=period, multi_level_index=False)
        
        if data.empty:
            raise ValueError("No historical data found. The symbol might be unlisted or incorrectly typed.")

        # Display key metrics using the detected currency symbol
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"{ticker} Current Price", value=f"{currency_symbol}{data['Close'].iloc[-1]:.2f}")
        with col2:
            price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
            st.metric(label="Period Change", value=f"{currency_symbol}{price_change:.2f}", delta=f"{currency_symbol}{price_change:.2f}")

        # Interactive Chart
        st.subheader(f"{ticker} Price History ({raw_currency})")
        st.line_chart(data['Close'])

        # Structured Data Table
        st.subheader("Raw Financial Data")
        st.dataframe(data.tail(10))

    except Exception as e:
        st.error(f"❌ Error fetching data for **{ticker}**.")
        st.info(
            "💡 **Quick Troubleshooting Tips:**\n"
            "- **For US Stocks:** Use direct letters (e.g., `AAPL`, `TSLA`, `MSFT`).\n"
            "- **For Indian Stocks (NSE):** You must add `.NS` at the end (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`).\n"
            "- **For Indian Stocks (BSE):** Add `.BO` at the end (e.g., `500325.BO`).\n"
            "- Make sure the selected time frame has active trading data available."
        )
