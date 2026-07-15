import streamlit as st
import yfinance as yf
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Global Financial Screener", page_icon="📊", layout="wide")

st.title("📊 Global Financial Screener Dashboard")
st.write("Analyze real-time market data across global exchanges smoothly.")

# --- SIDEBAR INTERFACE ---
st.sidebar.header("Screener Settings")
raw_ticker = st.sidebar.text_input("Enter Stock Ticker Symbol", value="AAPL")

# Clean input strings: trim white spaces and ensure uppercase conversion
ticker = raw_ticker.strip().upper()
period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "5y"])

st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Global Ticker Suffix Guide")
st.sidebar.write("Ensure you append the proper exchange suffix for foreign equities:")

# Structured guide mapping common global exchanges
exchange_data = {
    "Country/Region": ["United States", "India (NSE)", "India (BSE)", "United Kingdom", "Canada", "Germany", "Japan", "Australia"],
    "Suffix Required": ["None", ".NS", ".BO", ".L", ".TO", ".DE", ".T", ".AX"],
    "Example Ticker": ["AAPL", "RELIANCE.NS", "500325.BO", "BP.L", "SHOP.TO", "SAP.DE", "7203.T", "BHP.AX"]
}
df_exchanges = pd.DataFrame(exchange_data)
st.sidebar.dataframe(df_exchanges, hide_index=True)

# --- CORE PROCESSING ENGINE ---
if ticker:
    try:
        # Step 1: Download the historical chart data directly 
        data = yf.download(tickers=ticker, period=period)
        
        if data.empty:
            raise ValueError("No data returned. The symbol might be unlisted, delisted, or incorrectly typed.")

        # Step 2: Repair the structure by flattening any new multi-index column layers
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Uniformly clean column names to strip out structural discrepancies
        data.columns = [str(col).strip() for col in data.columns]

        # Step 3: Dynamic Currency Tracker According to the Market
        currency_symbol = "$" # Default to USD for US markets
        
        if ticker.endswith(".NS") or ticker.endswith(".BO") or ticker == "^NSEI" or ticker == "^BSESN":
            currency_symbol = "₹" # Indian Rupee
        elif ticker.endswith(".L"):
            currency_symbol = "£" # British Pound
        elif ticker.endswith(".DE") or ticker.endswith(".PA") or ticker.endswith(".AS"):
            currency_symbol = "€" # Euro
        elif ticker.endswith(".TO") or ticker.endswith(".V"):
            currency_symbol = "CA$" # Canadian Dollar
        elif ticker.endswith(".AX"):
            currency_symbol = "A$" # Australian Dollar
        elif ticker.endswith(".T"):
            currency_symbol = "¥" # Japanese Yen

        # Display key metrics safely with the correct local market currency
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f"{ticker} Current Price", value=f"{currency_symbol}{data['Close'].iloc[-1]:.2f}")
        with col2:
            price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
            st.metric(label="Period Change", value=f"{currency_symbol}{price_change:.2f}", delta=f"{currency_symbol}{price_change:.2f}")

        # Interactive Chart Render Component
        st.subheader(f"{ticker} Price History Time-Series")
        st.line_chart(data['Close'])

        # Structured Data Table Output
        st.subheader("Raw Financial Data (10 Most Recent Sessions)")
        st.dataframe(data.tail(10))

    except Exception as e:
        st.error(f"❌ Error fetching data for **{ticker}**.")
        st.info(
            f"💡 **Technical Detail:** {e}\n\n"
            "**Quick Fix Steps:**\n"
            "- Double-check that you entered a valid short **Ticker Symbol** (like `MSFT`), not the full company name.\n"
            "- Look at the **Global Ticker Suffix Guide** in the sidebar to check if your foreign asset requires an exchange suffix.\n"
            "- For market indexes, use a caret symbol at the front (e.g., `^NSEI` for Nifty 50 or `^BSESN` for Sensex)."
        )
