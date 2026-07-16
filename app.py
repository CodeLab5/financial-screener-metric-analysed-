import streamlit as st
import requests
import pandas as pd

# Page Configuration & Clean Universal Layout
st.set_page_config(page_title="Universal Financial Analytics", page_icon="🌐", layout="wide")

st.title("🌐 Universal Financial Analytics Database Dashboard")
st.write("Production-grade market engine powered by Alpha Vantage official database streaming.")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("🕹️ Global Database Control")

# Secure API Key input box so the code remains universal
api_key = st.sidebar.text_input("Enter Alpha Vantage API Key", type="password", value="")
raw_ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g., NTPC, AAPL, OR)", value="NTPC")
ticker = raw_ticker.strip().upper()

st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Alpha Vantage Search Rules")
st.sidebar.caption(
    "Because this queries a direct exchange database, you don't use dots! "
    "Use a colon for international markets:\n"
    "- India NSE -> `NSE:NTPC`\n"
    "- South Korea -> `KRX:005930`\n"
    "- France Paris -> `PAR:OR`\n"
    "- US Markets -> `AAPL` (No prefix needed)"
)

# --- ENGINE LAYER ---
if ticker and api_key:
    try:
        # Step 1: Query the Global Digital Database Endpoint
        # We use DAILY ADJUSTED data for clean dividend/split historical records
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={api_key}&outputsize=compact"
        response = requests.get(url)
        json_data = response.json()

        # Error Handling Layer for wrong tickers or API limits
        if "Error Message" in json_data:
            raise ValueError("Ticker notation not recognized by database. Please verify prefix rules.")
        if "Note" in json_data:
            st.warning("⚠️ Database API speed limit reached (5 requests/min max for free tier). Wait 60s.")
            st.stop()
        if "Time Series (Daily)" not in json_data:
            raise ValueError("Database returned an empty packet. Check your API Key.")

        # Step 2: DYNAMIC CURRENCY & GEOGRAPHY METADATA DETECTION
        # Real databases pass the exact currency in a fixed text metadata block cleanly!
        meta_data = json_data.get("Meta Data", {})
        
        # Sniff out the currency dynamically without hardcoding suffixes
        # Alpha Vantage provides currency context under standard string parameters
        detected_currency = "USD"
        for key, val in meta_data.items():
            if "currency" in key.lower():
                detected_currency = val
                break
        
        # Fallback check mapping common exchange prefixes if the metadata field is hidden
        if detected_currency == "USD" and ":" in ticker:
            prefix = ticker.split(":")[0]
            prefix_map = {"NSE": "INR", "BSE": "INR", "KRX": "KRW", "PAR": "EUR", "TSE": "JPY"}
            detected_currency = prefix_map.get(prefix, "USD")

        detected_currency = str(detected_currency).upper().strip()

        # Step 3: Parse Time Series JSON into a clean Pandas Data Array
        raw_series = json_data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(raw_series, orient="index")
        
        # Convert index strings to actual datetime timestamps
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Rename columns from Alpha Vantage string format ("4. close") to clean metrics
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adjusted_Close",
            "6. volume": "Volume"
        })

        # Ensure all numeric fields are forced to clean standard floats
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col])

        # Step 4: Universal Currencies Symbol Conversion Layer
        currency_symbols = {
            'USD': '$', 'INR': '₹', 'GBP': '£', 'EUR': '€', 'JPY': '¥', 
            'KRW': '₩', 'CAD': 'CA$', 'AUD': 'A$', 'HKD': 'HK$', 'CNY': '元', 
            'MAD': 'DH ', 'SGD': 'S$', 'CHF': 'CHF '
        }
        currency_symbol = currency_symbols.get(detected_currency, f"{detected_currency} ")

        # Step 5: Compute Core Metrics
        current_price = float(df['Close'].iloc[-1])
        initial_price = float(df['Close'].iloc[0])
        price_delta = current_price - initial_price
        pct_delta = (price_delta / initial_price) * 100

        # Technical Signal Indicator Calculations
        df['SMA_20'] = df['Close'].rolling(window=min(20, len(df))).mean()

        # --- VISUALIZATION LAYER ---
        st.info(f"🏛️ **Database Ledger:** Asset cleared in local sovereign currency: `{detected_currency}`")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"🎯 {ticker} Current Price", value=f"{currency_symbol}{current_price:,.2f}")
        with col2:
            st.metric(label="📊 Absolute Range Delta", value=f"{currency_symbol}{price_delta:,.2f}", delta=f"{price_delta:,.2f}")
        with col3:
            st.metric(label="⚡ Growth Performance Rate", value=f"{pct_delta:.2f}%", delta=f"{pct_delta:.2f}%")

        st.markdown("---")

        # Visual Analytics Component Chart
        st.subheader(f"📉 Historical Price Track & Technical 20-Day SMA Line ({ticker})")
        st.line_chart(df[['Close', 'SMA_20']])

        # Matrix View
        st.subheader("📁 Session Archive View (10 Most Recent Sessions)")
        st.dataframe(df.tail(10))

    except Exception as e:
        st.error(f"❌ Core processing error trying to stream data for **{ticker}**.")
        st.info(f"⚙️ **Database System Logs:** {e}")
        
elif not api_key:
    st.warning("🔑 Please enter your Alpha Vantage API Key in the left sidebar configuration panel to initialize the global database link.")
