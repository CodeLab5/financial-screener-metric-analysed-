import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration & Custom Theme Styling
st.set_page_config(page_title="Global Financial Analytics", page_icon="📈", layout="wide")

st.title("📈 Global Financial Analytics Dashboard")
st.write("Real-time data feeds, technical tracking parameters, and historical analytics arrays across global markets.")

# 2. Sidebar Layout Panel Controls
st.sidebar.header("🕹️ Configuration Control Panel")
raw_ticker = st.sidebar.text_input("Enter Stock Ticker Symbol", value="BEL.NS")
ticker = raw_ticker.strip().upper()
period = st.sidebar.selectbox("Lookback Time Horizon", ["1mo", "3mo", "6mo", "1y", "5y"])

st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Global Market Suffix Guide")
st.sidebar.write("Ensure you append the correct extension code for non-US securities:")

# Clean mapping directory for users
exchange_data = {
    "Region/Exchange": ["United States", "India (NSE)", "India (BSE)", "United Kingdom", "Canada", "Germany", "Japan", "Australia"],
    "Suffix Required": ["None", ".NS", ".BO", ".L", ".TO", ".DE", ".T", ".AX"],
    "Example Query": ["AAPL", "BEL.NS", "500325.BO", "BP.L", "SHOP.TO", "SAP.DE", "7203.T", "BHP.AX"]
}
st.sidebar.dataframe(pd.DataFrame(exchange_data), hide_index=True)

# 3. Core Processing Engine
if ticker:
    try:
        # Step A: Direct data stream download
        data = yf.download(tickers=ticker, period=period)
        
        if data.empty:
            raise ValueError("No records returned. The asset may be delisted, halted, or misspelled.")

        # Step B: Absolute MultiIndex column flattening to eliminate structural $nan bugs
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Clean string spaces off headers
        data.columns = [str(col).strip() for col in data.columns]

        # Step C: Drop rows missing core parameters (prevents timezone-based NaN parsing errors)
        data = data.dropna(subset=['Close'])

        # Step D: Comprehensive Market Suffix-Based Currency Mapping System
        currency_symbol = "$" # Default fallback standard
        
        if ticker.endswith(".NS") or ticker.endswith(".BO") or ticker in ["^NSEI", "^BSESN"]:
            currency_symbol = "₹"
        elif ticker.endswith(".L"):
            currency_symbol = "£"
        elif any(ticker.endswith(ext) for ext in [".DE", ".PA", ".AS", ".FR", ".IT"]):
            currency_symbol = "€"
        elif ticker.endswith(".TO") or ticker.endswith(".V"):
            currency_symbol = "CA$"
        elif ticker.endswith(".AX"):
            currency_symbol = "A$"
        elif ticker.endswith(".T"):
            currency_symbol = "¥"
        elif ticker.endswith(".HK"):
            currency_symbol = "HK$"

        # Step E: Isolate pricing numbers cleanly as simple floats to prevent Streamlit array rendering errors
        current_price = float(data['Close'].iloc[-1])
        initial_price = float(data['Close'].iloc[0])
        price_delta = current_price - initial_price
        pct_delta = (price_delta / initial_price) * 100

        # Step F: Mathematical Indicator Calculations (20-Day Simple Moving Average)
        data['SMA_20'] = data['Close'].rolling(window=min(20, len(data))).mean()

        # 4. Premium Graphical Presentation Interface Layout
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"🎯 {ticker} Current Price", value=f"{currency_symbol}{current_price:,.2f}")
        with col2:
            st.metric(label="📊 Absolute Session Delta", value=f"{currency_symbol}{price_delta:,.2f}", delta=f"{price_delta:,.2f}")
        with col3:
            st.metric(label="⚡ Growth Performance Rate", value=f"{pct_delta:.2f}%", delta=f"{pct_delta:.2f}%")

        st.markdown("---")

        # High-Impact Trend Charts Layer
        st.subheader("📉 Technical Pricing Trends (Closing Cost vs. 20-Day Simple Moving Average)")
        st.line_chart(data[['Close', 'SMA_20']])

        # Structured Data Table Output Panel
        st.subheader("📁 Complete Data Array View (10 Most Recent Market Sessions)")
        st.dataframe(data.tail(10))

    except Exception as e:
        st.error(f"❌ Core pipeline processing error for **{ticker}**.")
        st.info(
            f"⚙️ **System Diagnostic Logs:** {e}\n\n"
            "**Quick Remediation Steps:**\n"
            "- Ensure your input represents a **Ticker Symbol** (e.g., `MSFT`), not a formal company name.\n"
            "- Crosscheck your asset suffix matching rules against the **Global Market Suffix Guide** listed in the left sidebar layout.\n"
            "- For indexing parameters, lead with a caret notation (like `^NSEI` or `^GSPC`)."
        )
