import streamlit as st
import yfinance as yf
import pandas as pd

# Page Configuration & Clean Universal Layout
st.set_page_config(page_title="Universal Financial Analytics", page_icon="🌐", layout="wide")

st.title("🌐 Universal Financial Analytics Dashboard")
st.write("Real-time data engine providing coverage across all global exchanges, asset classes, and localized currencies.")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("🕹️ Global Control Interface")
raw_ticker = st.sidebar.text_input("Enter Ticker Symbol (Any Exchange)", value="NTPC.NS")
ticker = raw_ticker.strip().upper()
period = st.sidebar.selectbox("Lookback Horizon", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)

# Global Navigation Cheatsheet
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Sample Global Asset Index")
exchange_examples = {
    "Region / Country": ["United States", "India (NSE)", "China (Shanghai)", "Japan (Tokyo)", "South Korea", "Australia", "Morocco (Casablanca)", "Europe (Germany)"],
    "Market Suffix": ["None", ".NS", ".SS", ".T", ".KS", ".AX", ".CS", ".DE"],
    "Sample Ticker": ["AAPL", "NTPC.NS", "600519.SS", "7203.T", "005930.KS", "BHP.AX", "ATW.CS", "SAP.DE"]
}
st.sidebar.dataframe(pd.DataFrame(exchange_examples), hide_index=True)

# --- ENGINE LAYER ---
if ticker:
    try:
        # Step A: Smart Ticker Auto-Correction Mapping
        ticker_corrections = {
            "HUL": "HINDUNILVR.NS", "HUL.NS": "HINDUNILVR.NS",
            "HINDUSTAN UNILEVER": "HINDUNILVR.NS", "HINDUSTANUNILEVER.NS": "HINDUNILVR.NS",
            "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS", "NTPC": "NTPC.NS"
        }
        if ticker in ticker_corrections:
            ticker = ticker_corrections[ticker]

        # Step B: Download data immediately to ensure network connection is established
        data = yf.download(tickers=ticker, period=period, progress=False)
        
        if data.empty:
            raise ValueError(f"No pricing arrays found for '{ticker}'. Verify exchange suffix rules.")

        # Step C: Direct Global Currency Sniffer Engine
        detected_currency = None
        try:
            # Query the live ticker profile directly to fetch the exact currency logged by the local exchange
            ticker_obj = yf.Ticker(ticker)
            detected_currency = ticker_obj.fast_info.get('currency', None)
        except Exception:
            pass

        # Step D: Universal Suffix Backup Plan (If the exchange server experiences a metadata timeout)
        if not detected_currency:
            suffix_map = {
                '.NS': 'INR', '.BO': 'INR', '.L': 'GBP', '.DE': 'EUR', 
                '.PA': 'EUR', '.AS': 'EUR', '.FR': 'EUR', '.IT': 'EUR', 
                '.TO': 'CAD', '.V': 'CAD', '.AX': 'AUD', '.T': 'JPY', 
                '.KS': 'KRW', '.CS': 'MAD', '.SS': 'CNY', '.SZ': 'CNY', 
                '.HK': 'HKD', '.SG': 'SGD', '.MI': 'EUR', '.MC': 'EUR'
            }
            for suffix, curr in suffix_map.items():
                if ticker.endswith(suffix):
                    detected_currency = curr
                    break
            
            # Default fallback if absolutely no match is found anywhere
            if not detected_currency:
                detected_currency = 'USD'

        # Normalize currency string to uppercase
        detected_currency = str(detected_currency).upper()

        # Step E: Flatten MultiIndex columns out safely
        if isinstance(data.columns, pd.MultiIndex):
            if ticker in data.columns.get_level_values(1):
                data = data.xs(ticker, level=1, axis=1)
            else:
                data.columns = data.columns.get_level_values(0)
        
        data.columns = [str(col).strip() for col in data.columns]
        data = data.dropna(subset=['Close'])

        # Step F: Universal Currency Sign Matrix Mapping
        currency_symbols = {
            'USD': '$', 'INR': '₹', 'GBP': '£', 'EUR': '€', 
            'CAD': 'CA$', 'AUD': 'A$', 'JPY': '¥', 'KRW': '₩', 
            'HKD': 'HK$', 'CNY': '元', 'MAD': 'DH ', 'SGD': 'S$', 
            'CHF': 'CHF ', 'NZD': 'NZ$', 'ZAR': 'R ', 'BRL': 'R$'
        }
        currency_symbol = currency_symbols.get(detected_currency, f"{detected_currency} ")

        # Step G: Calculate Core Metrics
        current_price = float(data['Close'].iloc[-1])
        initial_price = float(data['Close'].iloc[0])
        price_delta = current_price - initial_price
        pct_delta = (price_delta / initial_price) * 100

        data['SMA_20'] = data['Close'].rolling(window=min(20, len(data))).mean()

        # --- VISUALIZATION LAYER ---
        st.info(f"🪙 **Sovereign Base Currency Identified:** `{detected_currency}`")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"🎯 {ticker} Current Price", value=f"{currency_symbol}{current_price:,.2f}")
        with col2:
            st.metric(label="📊 Absolute Range Delta", value=f"{currency_symbol}{price_delta:,.2f}", delta=f"{price_delta:,.2f}")
        with col3:
            st.metric(label="⚡ Growth Performance Rate", value=f"{pct_delta:.2f}%", delta=f"{pct_delta:.2f}%")

        st.markdown("---")

        st.subheader(f"📉 Historical Price Track & Technical 20-Day SMA Line ({ticker})")
        st.line_chart(data[['Close', 'SMA_20']])

        st.subheader("📁 Session Archive View (10 Most Recent Adjustments)")
        st.dataframe(data.tail(10))

    except Exception as e:
        st.error(f"❌ Core processing error trying to access tracking assets for **{ticker}**.")
        st.info(f"⚙️ **System Diagnostics:** {e}")
