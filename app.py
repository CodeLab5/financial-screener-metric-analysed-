import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Global Market & Risk Analytics Engine", 
    page_icon="📊", 
    layout="wide"
)

st.title("📊 Global Market Analytics & Quantitative Dashboard")
st.write("Real-time tracking of asset pricing, dynamic global currencies, and risk factors (Alpha & Beta).")
st.markdown("---")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("🕹️ Market Control Panel")
raw_ticker = st.sidebar.text_input("Enter Ticker Symbol", value="NTPC.NS")
ticker = raw_ticker.strip().upper()

benchmark_symbol = st.sidebar.text_input("Benchmark Symbol for Alpha/Beta", value="^NSEI")
period = st.sidebar.selectbox("Lookback Horizon", ["3mo", "6mo", "1y", "3y", "5y"], index=2)

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Common Benchmark Symbols:**\n"
    "• Global/US Benchmark: `^GSPC` (S&P 500)\n"
    "• India Benchmark: `^NSEI` (Nifty 50)\n"
    "• Tech Benchmark: `^IXIC` (Nasdaq)"
)

# --- HELPER DATA FUNCTIONS ---
def get_clean_prices(symbol, time_period):
    """Downloads prices and flattens MultiIndex columns if necessary."""
    df = yf.download(tickers=symbol, period=time_period, progress=False)
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        if symbol in df.columns.get_level_values(1):
            df = df.xs(symbol, level=1, axis=1)
        else:
            df.columns = df.columns.get_level_values(0)
    df.columns = [str(col).strip() for col in df.columns]
    return df.dropna(subset=['Close'])

# --- CORE ENGINE LAYER ---
if ticker:
    try:
        data = get_clean_prices(ticker, period)
        if data is None:
            st.error(f"❌ No active market records found for '{ticker}'. Check symbol notation.")
            st.stop()

        # Dynamic Currency Detection Engine
        detected_currency = "USD"
        ticker_obj = yf.Ticker(ticker)
        try:
            if hasattr(ticker_obj, 'history_metadata') and 'currency' in ticker_obj.history_metadata:
                detected_currency = ticker_obj.history_metadata['currency']
            elif hasattr(ticker_obj, 'fast_info') and 'currency' in ticker_obj.fast_info:
                detected_currency = ticker_obj.fast_info['currency']
        except Exception:
            pass
            
        if detected_currency == "USD" and "." in ticker:
            suffix = ticker.split(".")[-1]
            suffix_map = {
                'NS': 'INR', 'BO': 'INR', 'KS': 'KRW', 'PA': 'EUR', 
                'DE': 'EUR', 'L': 'GBP', 'T': 'JPY', 'AX': 'AUD', 'CS': 'MAD'
            }
            detected_currency = suffix_map.get(suffix, "USD")

        detected_currency = str(detected_currency).upper().strip()

        currency_symbols = {
            'USD': '$', 'INR': '₹', 'GBP': '£', 'EUR': '€', 'JPY': '¥', 
            'KRW': '₩', 'CAD': 'CA$', 'AUD': 'A$', 'MAD': 'DH '
        }
        currency_symbol = currency_symbols.get(detected_currency, f"{detected_currency} ")

        # Extract Pricing Metrics
        current_price = float(data['Close'].iloc[-1])
        initial_price = float(data['Close'].iloc[0])
        price_delta = current_price - initial_price
        pct_delta = (price_delta / initial_price) * 100

        # Technical Signal Overlay
        data['SMA_20'] = data['Close'].rolling(window=min(20, len(data))).mean()

        # Quantitative Metrics Engine: Alpha & Beta Calculation
        alpha_val, beta_val = None, None
        benchmark_data = get_clean_prices(benchmark_symbol, period)

        if benchmark_data is not None:
            # Combine daily percentage returns for aligned dates
            asset_returns = data['Close'].pct_change().dropna()
            bench_returns = benchmark_data['Close'].pct_change().dropna()

            aligned_df = pd.concat([asset_returns, bench_returns], axis=1, join='inner').dropna()
            aligned_df.columns = ['Asset', 'Benchmark']

            if len(aligned_df) > 20:
                cov_matrix = np.cov(aligned_df['Asset'], aligned_df['Benchmark'])
                covariance = cov_matrix[0][1]
                benchmark_variance = cov_matrix[1][1]

                # Beta = Covariance(Asset, Benchmark) / Variance(Benchmark)
                beta_val = covariance / benchmark_variance

                # Alpha = Annualized Asset Return - (Beta * Annualized Benchmark Return)
                trading_days = 252
                mean_asset_return = aligned_df['Asset'].mean() * trading_days
                mean_bench_return = aligned_df['Benchmark'].mean() * trading_days
                
                # Assuming 0% risk-free rate for simplified baseline excess return
                alpha_val = mean_asset_return - (beta_val * mean_bench_return)

        # --- VISUALIZATION LAYER ---
        st.success(f"🏛️ **Local Clearing Currency:** **{detected_currency}** ({currency_symbol})")

        # Row 1: Asset Price & Growth Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label=f"🎯 {ticker} Current Price", value=f"{currency_symbol}{current_price:,.2f}")
        with c2:
            st.metric(label="📊 Absolute Delta", value=f"{currency_symbol}{price_delta:,.2f}", delta=f"{price_delta:,.2f}")
        with c3:
            st.metric(label="⚡ Growth Performance Rate", value=f"{pct_delta:.2f}%", delta=f"{pct_delta:.2f}%")

        st.markdown("---")

        # Row 2: Quantitative Risk Factors
        st.subheader("📐 Risk & Portfolio Metrics")
        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric(
                label=f"📈 Beta (vs {benchmark_symbol})", 
                value=f"{beta_val:.2f}" if beta_val is not None else "N/A"
            )
        with q2:
            st.metric(
                label=f"🏆 Alpha (vs {benchmark_symbol})", 
                value=f"{alpha_val * 100:.2f}%" if alpha_val is not None else "N/A"
            )
        with q3:
            st.metric(
                label="⚙️ Active Risk Horizon", 
                value=f"{len(data)} Trading Sessions"
            )

        st.markdown("---")

        # Visual Analytics Component Chart
        st.subheader(f"📉 Historical Price Track & Technical 20-Day SMA Line ({ticker})")
        st.line_chart(data[['Close', 'SMA_20']])

        # Matrix View
        st.subheader("📁 Session Archive View (10 Most Recent Sessions)")
        st.dataframe(data.tail(10), use_container_width=True)

    except Exception as e:
        st.error("⚠️ **Data Processing Notice:** Unable to fully stream tracking datasets.")
        st.info(f"⚙️ **System Diagnostics:** {e}")
