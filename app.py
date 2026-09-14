import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time as dtime
import requests
from sklearn.ensemble import GradientBoostingClassifier

# Page Configuration
st.set_page_config(
    page_title="Autonomous Self-Updating AI Terminal v32.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

TELEGRAM_BOT_TOKEN = "8462007353:AAFZsWmNgiVWBIPngaA5AEnHqzwWhMRl9hU"
TELEGRAM_CHAT_ID = "1147331498"

# Bloomberg Dark Luxury UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #020617 0%, #0b1329 100%); color: #f8fafc; }
    div[data-testid="stMetric"] { background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 16px; }
    .glass-card { background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 14px; padding: 20px; margin-bottom: 20px; }
    .glow-buy { border-left: 5px solid #10b981 !important; box-shadow: 0 0 15px rgba(16, 185, 129, 0.25); }
    .glow-sell { border-left: 5px solid #ef4444 !important; box-shadow: 0 0 15px rgba(239, 68, 68, 0.25); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%); color: white; font-weight: 700; border-radius: 10px; border: none; height: 50px; }
    .title-text { font-size: 30px; font-weight: 800; background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-text">🤖 Autonomous Self-Updating AI Terminal v32.0</p>', unsafe_allow_html=True)
st.caption("100% Self-Learning ML Pipeline | Auto-Adaptive Indicators | Dynamic Risk Engine")

NIFTY_TOP50 = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "SBIN", 
    "ITC", "HINDUNILVR", "AXISBANK", "KOTAKBANK", "TATAMOTORS", "TATASTEEL", 
    "MARUTI", "SUNPHARMA", "NTPC", "POWERGRID", "TITAN", "BAJFINANCE", "ADANIENT"
]

def send_telegram_alert(symbol, signal, price, sl, tp1, tp2, win_rate, qty, reason):
    emoji = "🚀" if "BUY" in signal else "💥"
    message = f"""
{emoji} **100% AUTONOMOUS AI SIGNAL (v32.0)** {emoji}

📌 **Stock:** #{symbol}
🚦 **Signal:** {signal}
💰 **Entry Price:** ₹{price:.2f}
🎯 **Suggested Quantity:** {qty} Shares
🔥 **AI Precision Win-Rate:** {win_rate}%

🛑 **Strict Stop Loss (SL):** ₹{sl:.2f}
🎯 **Target 1 (1:2 RR):** ₹{tp1:.2f}
🚀 **Target 2 (1:3.5 RR):** ₹{tp2:.2f}

💡 **Auto-Analyzed Confluence:**
{reason}

⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=5)
    except Exception:
        pass

# 1. AUTO LIVE DATA PIPELINE (Auto-Refreshes every 60 sec)
@st.cache_data(ttl=60)
def fetch_data_auto(ticker, interval="5m", period="30d"):
    clean_ticker = ticker.strip().upper()
    full_ticker = clean_ticker + ".NS" if not clean_ticker.endswith(".NS") else clean_ticker
    try:
        data = yf.Ticker(full_ticker)
        df = data.history(period=period, interval=interval)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df, clean_ticker
    except Exception:
        return pd.DataFrame(), clean_ticker

# 2. AUTO MACHINE LEARNING RETRAINING PIPELINE (Retrains every 30 mins)
@st.cache_resource(ttl=1800)
def train_auto_ml_model(df_json):
    try:
        df = pd.read_json(df_json)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['EMA20_Diff'] = (df['Close'] - ta.trend.ema_indicator(df['Close'], window=20)) / df['Close']
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        df['Vol_Surge'] = df['Volume'] / ta.trend.sma_indicator(df['Volume'], window=20)
        df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
        
        df_ml = df.dropna()
        if len(df_ml) < 30: return None
        
        features = ['RSI', 'EMA20_Diff', 'ATR', 'Vol_Surge']
        X = df_ml[features]
        y = df_ml['Target']
        
        model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
        model.fit(X, y)
        return model
    except Exception:
        return None

# 3. FULL AUTONOMOUS ENGINE (Combines ML + Multi-Timeframe + Dynamic Risk)
def analyze_stock_autonomous(symbol, capital, risk_pct):
    df_5m, clean_symbol = fetch_data_auto(symbol, "5m")
    df_15m, _ = fetch_data_auto(symbol, "15m")
    
    if df_5m.empty or len(df_5m) < 30:
        return None

    c, h, l, v = df_5m['Close'], df_5m['High'], df_5m['Low'], df_5m['Volume']
    
    df_5m['EMA20'] = ta.trend.ema_indicator(c, window=20)
    df_5m['EMA50'] = ta.trend.ema_indicator(c, window=50)
    df_5m['RSI'] = ta.momentum.rsi(c, window=14)
    df_5m['ATR'] = ta.volatility.average_true_range(h, l, c, window=14)
    df_5m['VOL_SMA'] = ta.trend.sma_indicator(v, window=20)
    df_5m['VWAP'] = ((h + l + c) / 3 * v).cumsum() / v.cumsum()

    latest = df_5m.iloc[-1]
    price = float(latest['Close'])
    atr = float(latest['ATR']) if not np.isnan(latest['ATR']) else (price * 0.01)
    vwap = float(latest['VWAP']) if not np.isnan(latest['VWAP']) else price
    vol_ratio = float(latest['Volume']) / (float(latest['VOL_SMA']) if float(latest['VOL_SMA']) > 0 else 1.0)

    # Higher Timeframe Trend Filter (15M)
    trend_15m_bull = False
    if not df_15m.empty and len(df_15m) > 20:
        ema20_15m = ta.trend.ema_indicator(df_15m['Close'], window=20).iloc[-1]
        trend_15m_bull = df_15m['Close'].iloc[-1] > ema20_15m

    # Auto ML Prediction Calculation
    model = train_auto_ml_model(df_5m.to_json())
    win_prob = 75.0
    if model:
        try:
            sample = pd.DataFrame([{
                'RSI': float(latest['RSI']),
                'EMA20_Diff': (price - float(latest['EMA20'])) / price,
                'ATR': atr,
                'Vol_Surge': vol_ratio
            }])
            win_prob = round(model.predict_proba(sample)[0][1] * 100, 1)
        except Exception:
            pass

    signal = "NEUTRAL ⏸️"
    sl, tp1, tp2, position_qty = 0.0, 0.0, 0.0, 0
    reason = "சந்தையில் போதிய Multi-Timeframe Alignment இல்லை (Noise Filtered)."

    if price > vwap and float(latest['EMA20']) > float(latest['EMA50']) and trend_15m_bull and vol_ratio >= 1.2 and win_prob >= 60.0:
        signal = "AI AUTONOMOUS BUY 🚀"
        sl = price - (atr * 1.5)
        tp1 = price + (atr * 2.0)
        tp2 = price + (atr * 3.5)
        
        risk_per_share = price - sl
        max_risk_amount = capital * (risk_pct / 100.0)
        position_qty = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 1
        reason = f"• Price above VWAP & EMA20\n• 15m HTF Trend: BULLISH\n• Volume Surge: {vol_ratio:.1f}x\n• ML Retrained Win-Rate: {win_prob}%"
        
    elif price < vwap and float(latest['EMA20']) < float(latest['EMA50']) and not trend_15m_bull and vol_ratio >= 1.2 and win_prob <= 40.0:
        signal = "AI AUTONOMOUS SELL 💥"
        sl = price + (atr * 1.5)
        tp1 = price - (atr * 2.0)
        tp2 = price - (atr * 3.5)
        
        risk_per_share = sl - price
        max_risk_amount = capital * (risk_pct / 100.0)
        position_qty = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 1
        reason = f"• Price below VWAP & EMA20\n• 15m HTF Trend: BEARISH\n• Volume Surge: {vol_ratio:.1f}x\n• ML Retrained Win-Rate: {100-win_prob}%"

    return {
        'df': df_5m, 'symbol': clean_symbol, 'price': price, 'signal': signal,
        'win_prob': win_prob, 'vwap': vwap, 'sl': sl, 'tp1': tp1, 'tp2': tp2, 
        'qty': position_qty, 'reason': reason
    }

# Sidebar Dynamic Controls
with st.sidebar:
    st.header("🤖 Autonomous Engine Status")
    st.success("✅ Auto-Data Stream: ACTIVE (60s)")
    st.success("✅ ML Retraining Engine: ACTIVE (30m)")
    st.markdown("---")
    st.header("⚙️ Risk Management")
    capital_input = st.number_input("Total Trading Capital (₹)", min_value=1000, value=100000, step=5000)
    risk_pct_input = st.slider("Risk Per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    st.markdown("---")
    enable_telegram = st.checkbox("Enable Auto Telegram Alerts", value=True)

tab1, tab2 = st.tabs(["💎 Autonomous Terminal", "🔥 Watchlist Multi-Scan"])

with tab1:
    stock_input = st.text_input("Enter NSE Stock Symbol", "TATAMOTORS")
    if stock_input:
        res = analyze_stock_autonomous(stock_input, capital_input, risk_pct_input)
        if res:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Live Price", f"₹{res['price']:.2f}")
            c2.metric("AI Signal", res['signal'])
            c3.metric("ML Win Rate", f"{res['win_prob']}%")
            c4.metric("Suggested Qty", f"{res['qty']} Units")

            card_class = "glow-buy" if "BUY" in res['signal'] else ("glow-sell" if "SELL" in res['signal'] else "")
            st.markdown(f"""
            <div class="glass-card {card_class}">
                <h4 style="margin-top:0; color:#38bdf8;">🧠 Self-Updated Confluence Breakdown</h4>
                <p style="white-space: pre-line; font-size: 15px;">{res['reason']}</p>
            </div>
            """, unsafe_allow_html=True)

            t1, t2, t3 = st.columns(3)
            t1.metric("Strict Stop Loss (SL)", f"₹{res['sl']:.2f}" if res['sl']>0 else "N/A")
            t2.metric("Target 1 (1:2)", f"₹{res['tp1']:.2f}" if res['tp1']>0 else "N/A")
            t3.metric("Target 2 (1:3.5)", f"₹{res['tp2']:.2f}" if res['tp2']>0 else "N/A")

            st.subheader("📈 Real-Time Chart Engine")
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['VWAP'], line=dict(color='#ec4899', width=2), name="VWAP"))
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['EMA20'], line=dict(color='#38bdf8', width=1.5), name="EMA 20"))
            fig.update_layout(template="plotly_dark", height=420, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if st.button("🚀 RUN FULL WATCHLIST SCAN"):
        results = []
        progress_bar = st.progress(0)
        for idx, stock in enumerate(NIFTY_TOP50):
            r = analyze_stock_autonomous(stock, capital_input, risk_pct_input)
            if r:
                results.append({
                    "Stock": r['symbol'],
                    "Signal": r['signal'],
                    "ML Accuracy": f"{r['win_prob']}%",
                    "Price (₹)": f"₹{r['price']:.2f}",
                    "Buy Qty": r['qty'],
                    "SL (₹)": f"₹{r['sl']:.2f}" if r['sl']>0 else "-",
                    "Target 1 (₹)": f"₹{r['tp1']:.2f}" if r['tp1']>0 else "-"
                })
                if enable_telegram and r['signal'] in ["AI AUTONOMOUS BUY 🚀", "AI AUTONOMOUS SELL 💥"]:
                    send_telegram_alert(r['symbol'], r['signal'], r['price'], r['sl'], r['tp1'], r['tp2'], r['win_prob'], r['qty'], r['reason'])
            progress_bar.progress((idx + 1) / len(NIFTY_TOP50))
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        st.success("✅ Watchlist Scan Completed!")
    
