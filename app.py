import streamlit as st
import yfinance as yf
import pandas as pd

# Set up stunning professional layout
st.set_page_config(page_title="Global Financial Analytics", page_icon="📈", layout="wide")

# Custom CSS styling for a cleaner modern look
st.markdown("""
    <style>
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    h1 { color: #FF4B4B; }
    </style>
""", unsafe_rule_allowed=True)

st.title("📈 Global Financial Analytics Dashboard")
st.write("Real-time data streams, technical indicators, and historical logs across worldwide exchanges.")

# --- SIDEBAR INTERFACE ---
st.sidebar.header("🕹️ Control Panel")
raw_ticker = st.sidebar.text_input("Stock Ticker Symbol", value="BEL.NS")
ticker = raw_ticker.strip().upper()
period = st.sidebar.selectbox("Analysis Lookback Horizon", ["1mo", "3mo", "6mo", "1y", "5y"])

st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Exchange Directory Cheatsheet")
exchange_data = {
    "Region": ["USA", "India (NSE)", "India (BSE)", "UK (London)", "Canada", "Germany", "Japan"],
    "Suffix": ["None", ".NS", ".BO", ".L", ".TO", ".DE", ".T"],
    "Example": ["AAPL", "BEL.NS", "500325.BO", "BP.L", "SHOP.TO", "SAP.DE", "7203.T"]
}
st.sidebar.dataframe(pd.DataFrame(exchange_data), hide_index=True)

# --- ENGINE & VISUALIZATION LAYER ---
if ticker:
    try:
        # 1. Pull Raw Market Matrix Data
        data = yf.download(tickers=ticker, period=period)
        
        if data.empty:
            raise ValueError("Empty response matrix. The stock ticker is either invalid or delisted.")

        # 2. Structural Index Flattening
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data.columns = [str(col).strip() for col in data.columns]

        # 3. CRITICAL REPAIR: Scrub NaN anomalies from live feeds
        data = data.dropna(subset=['Close', 'Open', 'High', 'Low'])

        # 4. Smart Currency Market Context Scanner
        currency_symbol = "$" 
        if any(suffix in ticker for suffix in [".NS", ".BO", "^NSEI", "^BSESN"]):
            currency_symbol = "₹"
        elif ".L" in ticker:
            currency_symbol = "£"
        elif any(suffix in ticker for suffix in [".DE", ".PA", ".AS"]):
            currency_symbol = "€"
        elif ".TO" in ticker or ".V" in ticker:
            currency_symbol = "CA$"
        elif ".T" in ticker:
            currency_symbol = "¥"

        # 5. Calculate Advanced Analytics (Visual Moving Averages)
        data['SMA_20'] = data['Close'].rolling(window=min(20, len(data))).mean()

        # Capture terminal pricing metrics safely
        current_price = data['Close'].iloc[-1]
        initial_price = data['Close'].iloc[0]
        price_delta = current_price - initial_price
        pct_delta = (price_delta / initial_price) * 100

        # --- GRAPHICAL PRESENTATION LAYER ---
        # High-impact metric scorecards
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label=f"🎯 {ticker} Current Close", value=f"{currency_symbol}{current_price:,.2f}")
        with m_col2:
            st.metric(label="📊 Absolute Delta", value=f"{currency_symbol}{price_delta:,.2f}", delta=f"{price_delta:,.2f}")
        with m_col3:
            st.metric(label="⚡ Growth Velocity", value=f"{pct_delta:.2f}%", delta=f"{pct_delta:.2f}%")

        st.markdown("---")

        # Premium interactive comparative trend graph
        st.subheader("📉 Technical Trend Analysis (Close vs. 20-Day Simple Moving Average)")
        chart_data = data[['Close', 'SMA_20']]
        st.line_chart(chart_data)

        # Tabbed display layouts separating structural views
        tab1, tab2 = st.tabs(["📁 Data Arrays", "🗒️ Summary Matrix"])
        with tab1:
            st.dataframe(data.tail(15).style.format({
                'Open': f'{currency_symbol}{{:.2f}}',
                'High': f'{currency_symbol}{{:.2f}}',
                'Low': f'{currency_symbol}{{:.2f}}',
                'Close': f'{currency_symbol}{{:.2f}}',
                'SMA_20': f'{currency_symbol}{{:.2f}}',
                'Volume': '{:,.0f}'
            }))
        with tab2:
            st.dataframe(data.describe())

    except Exception as e:
        st.error(f"❌ Core processing error for ticker **{ticker}**.")
        st.info(f"⚙️ **System Diagnostics:** {e}")
