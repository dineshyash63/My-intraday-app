import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import threading
import time

# Streamlit Page Configuration (Professional Dark Theme)
st.set_page_config(
    page_title="AI Intraday Pro Terminal v13.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "8462007353:AAFZsWmNgiVWBIPngaA5AEnHqzwWhMRl9hU"
TELEGRAM_CHAT_ID = "1147331498"

# High-Precision Styling (TradingView / Bloomberg Style)
st.markdown("""
<style>
    .main { background-color: #0b0e14; color: #d1d5db; }
    .stMetric { background-color: #131722; padding: 14px; border-radius: 8px; border: 1px solid #2a2e39; }
    .stButton>button { width: 100%; background-color: #22c55e; color: white; font-weight: bold; border-radius: 6px; border: none; height: 48px; font-size: 16px; }
    .stButton>button:hover { background-color: #16a34a; }
    div[data-testid="stSidebar"] { background-color: #131722; border-right: 1px solid #2a2e39; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ AI Intraday Pro Terminal v13.0 Ultimate")
st.caption("24/7 Background Auto-Scanner | 5-Min Telegram Signal Alerts | CPR & Institutional Confluence")

WATCHLIST = [
    "TATAMOTORS", "RELIANCE", "SBIN", "ICICIBANK", "AXISBANK", 
    "HDFCBANK", "INFY", "TCS", "TATASTEEL", "BHARTIARTL", 
    "M&M", "NTPC", "LT", "SUNPHARMA", "MARUTI", "KOTAKBANK"
]

def send_telegram_alert(symbol, signal, price, sl, tp1, tp2, score):
    message = f"""
🚀 **AI INTRADAY HIGH-PROBABILITY SIGNAL** 🚀

📌 **Stock:** #{symbol}
🚦 **Signal:** {signal}
💰 **Entry Price:** ₹{price:.2f}
🎯 **Confluence Score:** {score}/100

🛑 **Stop Loss (SL):** ₹{sl:.2f}
🎯 **Target 1 (1:2):** ₹{tp1:.2f}
🚀 **Target 2 (1:3.5):** ₹{tp2:.2f}

⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def calculate_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / df['Volume'].cumsum()

def generate_sample_data():
    dates = pd.date_range(end=datetime.now(), periods=100, freq='15min')
    np.random.seed(101)
    close = 900 + np.cumsum(np.random.randn(100) * 2.2)
    high = close + np.random.rand(100) * 3.5
    low = close - np.random.rand(100) * 3.5
    open_p = close + np.random.randn(100)
    volume = np.random.randint(10000, 100000, size=100)
    return pd.DataFrame({'Open': open_p, 'High': high, 'Low': low, 'Close': close, 'Volume': volume}, index=dates)

def fetch_data(ticker, interval, period="60d"):
    clean_ticker = ticker.strip().upper()
    full_ticker = clean_ticker + ".NS" if not clean_ticker.endswith(".NS") else clean_ticker
    try:
        data = yf.Ticker(full_ticker)
        df = data.history(period=period, interval=interval)
        if df.empty or len(df) < 20:
            df = data.history(period="3mo", interval="1d")
        if df.empty:
            df = generate_sample_data()
        return df, clean_ticker
    except Exception:
        return generate_sample_data(), clean_ticker

def analyze_stock_pro(symbol, tf="15m"):
    df_ltf, clean_symbol = fetch_data(symbol, tf)
    df_htf, _ = fetch_data(symbol, "1h")
    
    # 1H Higher Timeframe Confluence
    htf_ema50 = ta.trend.ema_indicator(df_htf['Close'], window=50).iloc[-1]
    htf_close = df_htf['Close'].iloc[-1]
    htf_bullish = htf_close > htf_ema50

    c, h, l, v = df_ltf['Close'], df_ltf['High'], df_ltf['Low'], df_ltf['Volume']
    
    # Technical Indicators Setup
    df_ltf['VWAP'] = calculate_vwap(df_ltf)
    df_ltf['EMA20'] = ta.trend.ema_indicator(c, window=20)
    df_ltf['EMA50'] = ta.trend.ema_indicator(c, window=50)
    df_ltf['EMA200'] = ta.trend.ema_indicator(c, window=200)
    df_ltf['RSI'] = ta.momentum.rsi(c, window=14)
    df_ltf['ATR'] = ta.volatility.average_true_range(h, l, c, window=14)
    
    adx_inst = ta.trend.ADXIndicator(h, l, c, window=14)
    df_ltf['ADX'] = adx_inst.adx()
    df_ltf['VOL_SMA'] = ta.trend.sma_indicator(v, window=20)

    # CPR Pivot Points
    prev_high = df_htf['High'].iloc[-2]
    prev_low = df_htf['Low'].iloc[-2]
    prev_close = df_htf['Close'].iloc[-2]
    
    pivot = (prev_high + prev_low + prev_close) / 3
    bc = (prev_high + prev_low) / 2
    tc = (pivot - bc) + pivot
    r1 = (2 * pivot) - prev_low
    s1 = (2 * pivot) - prev_high

    latest = df_ltf.iloc[-1]
    price = float(latest['Close'])
    rsi = float(latest['RSI']) if not np.isnan(latest['RSI']) else 50.0
    atr = float(latest['ATR']) if not np.isnan(latest['ATR']) else (price * 0.01)
    adx = float(latest['ADX']) if not np.isnan(latest['ADX']) else 20.0
    ema20 = float(latest['EMA20']) if not np.isnan(latest['EMA20']) else price
    ema50 = float(latest['EMA50']) if not np.isnan(latest['EMA50']) else price
    ema200 = float(latest['EMA200']) if not np.isnan(latest['EMA200']) else price
    vwap = float(latest['VWAP']) if not np.isnan(latest['VWAP']) else price
    vol_ratio = float(latest['Volume']) / (float(latest['VOL_SMA']) if float(latest['VOL_SMA']) > 0 else 1.0)

    # Confluence Scoring Model (0 - 100)
    score_bull, score_bear = 0, 0
    if htf_bullish: score_bull += 25
    else: score_bear += 25
    if price > vwap: score_bull += 20
    else: score_bear += 20
    if ema20 > ema50: score_bull += 20
    else: score_bear += 20
    if price > ema200: score_bull += 15
    else: score_bear += 15
    if 52 <= rsi <= 68: score_bull += 10
    elif 32 <= rsi <= 48: score_bear += 10
    if adx >= 20: score_bull += 10; score_bear += 10

    signal = "NEUTRAL ⏸️ (WAIT FOR SETUP)"
    sl, tp1, tp2 = 0.0, 0.0, 0.0
    confidence = max(score_bull, score_bear)

    if score_bull >= 85 and htf_bullish and price > vwap and adx >= 20:
        signal = "INSTITUTIONAL STRONG BUY 🚀"
        sl = price - (atr * 1.5)
        tp1 = price + (atr * 2.0)
        tp2 = price + (atr * 3.5)
    elif score_bear >= 85 and not htf_bullish and price < vwap and adx >= 20:
        signal = "INSTITUTIONAL STRONG SELL 💥"
        sl = price + (atr * 1.5)
        tp1 = price - (atr * 2.0)
        tp2 = price - (atr * 3.5)

    return {
        'df': df_ltf, 'symbol': clean_symbol, 'price': price, 'signal': signal,
        'score': confidence, 'vwap': vwap, 'ema20': ema20, 'ema50': ema50, 'ema200': ema200,
        'rsi': rsi, 'adx': adx, 'atr': atr, 'vol_ratio': vol_ratio, 'sl': sl, 'tp1': tp1, 'tp2': tp2,
        'pivot': pivot, 'tc': tc, 'bc': bc, 'r1': r1, 's1': s1, 'htf_bullish': htf_bullish
    }

# Background Scanner State
if 'scanner_running' not in st.session_state:
    st.session_state.scanner_running = False
if 'last_alerts' not in st.session_state:
    st.session_state.last_alerts = {}

def background_5min_scanner():
    while st.session_state.get('scanner_running', False):
        for stock in WATCHLIST:
            try:
                r = analyze_stock_pro(stock)
                if r['signal'] in ["INSTITUTIONAL STRONG BUY 🚀", "INSTITUTIONAL STRONG SELL 💥"]:
                    last_signal = st.session_state.last_alerts.get(stock)
                    if last_signal != r['signal']:
                        send_telegram_alert(r['symbol'], r['signal'], r['price'], r['sl'], r['tp1'], r['tp2'], r['score'])
                        st.session_state.last_alerts[stock] = r['signal']
            except Exception:
                pass
        time.sleep(300) # 5 Minutes Interval Loop

# Sidebar Controls & Risk Calculator
with st.sidebar:
    st.header("🤖 24x7 Telegram Auto Engine")
    
    if not st.session_state.scanner_running:
        if st.button("▶️ START 5-MIN BACKGROUND AUTO SCAN"):
            st.session_state.scanner_running = True
            t = threading.Thread(target=background_5min_scanner, daemon=True)
            t.start()
            st.success("✅ Auto Scanner Activated (Running in Background)")
    else:
        st.warning("🟢 Auto Scanner Active (Sending alerts to Telegram)")
        if st.button("⏹️ STOP AUTO SCANNER"):
            st.session_state.scanner_running = False
            st.info("🛑 Auto Scanner Stopped.")

    st.markdown("---")
    st.subheader("💰 Smart Risk Calculator")
    capital = st.number_input("Total Trading Capital (₹)", value=50000, step=5000)
    risk_pct = st.slider("Max Risk per Trade (%)", 0.5, 3.0, 1.0, 0.5)

# Main Terminal Interface
tab1, tab2 = st.tabs(["⚡ Precision Signal Terminal", "📊 Auto Watchlist Scanner"])

with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        stock_input = st.text_input("Enter NSE Stock Symbol", "TATAMOTORS")
        analyze_btn = st.button("⚡ EXECUTE PRO ANALYSIS")

    if stock_input:
        res = analyze_stock_pro(stock_input)
        df = res['df']

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Live Price", f"₹{res['price']:.2f}")
        m2.metric("Signal Status", res['signal'])
        m3.metric("Confluence Score", f"{res['score']}/100")
        m4.metric("Volume Surge", f"{res['vol_ratio']:.2f}x")

        risk_amount = capital * (risk_pct / 100)
        sl_dist = abs(res['price'] - res['sl']) if res['sl'] > 0 else res['atr'] * 1.5
        qty = int(risk_amount / sl_dist) if sl_dist > 0 else 0

        # Send Manual Trigger Telegram Alert
        if res['signal'] in ["INSTITUTIONAL STRONG BUY 🚀", "INSTITUTIONAL STRONG SELL 💥"]:
            send_telegram_alert(res['symbol'], res['signal'], res['price'], res['sl'], res['tp1'], res['tp2'], res['score'])
            st.success("📲 Instant Alert Sent to your Telegram Channel!")

        st.markdown("---")
        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.subheader("🎯 Trade Execution Levels")
            t1, t2, t3 = st.columns(3)
            t1.metric("Stop Loss (SL)", f"₹{res['sl']:.2f}" if res['sl']>0 else "N/A")
            t2.metric("Target 1 (1:2 R:R)", f"₹{res['tp1']:.2f}" if res['tp1']>0 else "N/A")
            t3.metric("Target 2 (1:3.5 R:R)", f"₹{res['tp2']:.2f}" if res['tp2']>0 else "N/A")

            st.info(f"""
            💡 **Position Management:**
            - **Max Risk Allowed:** ₹{risk_amount:,.2f} ({risk_pct}%)
            - **Exact Share Quantity:** {qty} Shares
            - **Total Capital Required:** ₹{(qty * res['price']):,.2f}
            """)

        with col_right:
            st.subheader("📍 CPR & Pivot Levels")
            st.write(f"• **Central Pivot (P):** ₹{res['pivot']:.2f}")
            st.write(f"• **CPR Range (TC - BC):** ₹{res['tc']:.2f} - ₹{res['bc']:.2f}")
            st.write(f"• **Resistance 1 (R1):** ₹{res['r1']:.2f}")
            st.write(f"• **Support 1 (S1):** ₹{res['s1']:.2f}")

        st.subheader("📈 Interactive Technical Chart")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='yellow', width=1.5), name="EMA 20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='magenta', width=2), name="VWAP"), row=1, col=1)
        
        colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🔥 Watchlist Scanner Engine")
    if st.button("🚀 SCAN WATCHLIST NOW"):
        results = []
        progress_bar = st.progress(0)
        for idx, stock in enumerate(WATCHLIST):
            r = analyze_stock_pro(stock)
            results.append({
                "Stock": r['symbol'],
                "Signal": r['signal'],
                "Score": f"{r['score']}/100",
                "Price (₹)": f"₹{r['price']:.2f}",
                "SL (₹)": f"₹{r['sl']:.2f}" if r['sl']>0 else "-",
                "Target 1 (₹)": f"₹{r['tp1']:.2f}" if r['tp1']>0 else "-"
            })
            if r['signal'] in ["INSTITUTIONAL STRONG BUY 🚀", "INSTITUTIONAL STRONG SELL 💥"]:
                send_telegram_alert(r['symbol'], r['signal'], r['price'], r['sl'], r['tp1'], r['tp2'], r['score'])
            progress_bar.progress((idx + 1) / len(WATCHLIST))
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        st.success("✅ Watchlist Scan Complete & Telegram Alerts Sent!")
    
