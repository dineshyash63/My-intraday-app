import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(page_title="AI Intraday Pro Terminal v6.0", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Premium Terminal Look
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e222d; padding: 12px; border-radius: 8px; border: 1px solid #2a2e39; }
    .stButton>button { width: 100%; background-color: #2962ff; color: white; font-weight: bold; border-radius: 6px; border: none; height: 45px; }
    .stButton>button:hover { background-color: #1e4bd8; }
    div[data-testid="stSidebar"] { background-color: #131722; border-right: 1px solid #2a2e39; }
</style>
""", unsafe_allow_html=True)

st.title("👑 AI Intraday Pro Terminal v6.0 (Institutional Grade)")
st.caption("Live Multi-Confluence Engine | TradingView Charts | Auto Multi-Scanner | Position Sizer | Pivot Points")

# Default Watchlist
WATCHLIST = [
    "TATAMOTORS", "RELIANCE", "SBIN", "ICICIBANK", "AXISBANK", 
    "HDFCBANK", "INFY", "TCS", "TATASTEEL", "BHARTIARTL", 
    "M&M", "NTPC", "LT", "SUNPHARMA", "MARUTI"
]

def calculate_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    vwap = (tp * df['Volume']).cumsum() / df['Volume'].cumsum()
    return vwap

def calculate_pivots(df):
    last_day = df.iloc[-1]
    h, l, c = last_day['High'], last_day['Low'], last_day['Close']
    p = (h + l + c) / 3
    r1 = (2 * p) - l
    s1 = (2 * p) - h
    r2 = p + (h - l)
    s2 = p - (h - l)
    return p, r1, s1, r2, s2

def analyze_stock(ticker_symbol, tf):
    ticker_clean = ticker_symbol.strip().upper()
    ticker_ns = ticker_clean + ".NS" if not ticker_clean.endswith(".NS") else ticker_clean
    
    try:
        data = yf.Ticker(ticker_ns)
        # 1mo period is safer for weekend data retrieval
        df = data.history(period="1mo", interval=tf)
        
        if df.empty or len(df) < 10:
            return None
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        df['VWAP'] = calculate_vwap(df)
        df['EMA20'] = ta.trend.ema_indicator(close, window=20)
        df['EMA50'] = ta.trend.ema_indicator(close, window=50)
        df['RSI'] = ta.momentum.rsi(close, window=14)
        df['ATR'] = ta.volatility.average_true_range(high, low, close, window=14)
        
        macd_obj = ta.trend.MACD(close)
        df['MACD'] = macd_obj.macd()
        df['MACD_SIG'] = macd_obj.macd_signal()
        df['VOL_SMA'] = ta.trend.sma_indicator(volume, window=20)
        
        latest = df.iloc[-1]
        price = float(latest['Close'])
        rsi = float(latest['RSI']) if not np.isnan(latest['RSI']) else 50.0
        atr = float(latest['ATR']) if not np.isnan(latest['ATR']) else 2.0
        ema20 = float(latest['EMA20']) if not np.isnan(latest['EMA20']) else price
        ema50 = float(latest['EMA50']) if not np.isnan(latest['EMA50']) else price
        vwap = float(latest['VWAP']) if not np.isnan(latest['VWAP']) else price
        macd_val = float(latest['MACD']) if not np.isnan(latest['MACD']) else 0.0
        macd_sig = float(latest['MACD_SIG']) if not np.isnan(latest['MACD_SIG']) else 0.0
        curr_vol = float(latest['Volume'])
        avg_vol = float(latest['VOL_SMA']) if not np.isnan(latest['VOL_SMA']) and latest['VOL_SMA'] > 0 else 1.0
        vol_ratio = curr_vol / avg_vol
        
        # Institutional Confluence Scoring Algorithm (0 - 100)
        score = 0
        if ema20 > ema50 and price > vwap: score += 30
        elif ema20 < ema50 and price < vwap: score += 30
        
        if vol_ratio >= 1.5: score += 25
        elif vol_ratio >= 1.0: score += 15
        
        if (atr / price) * 100 >= 0.5: score += 15
        if 40 <= rsi <= 65: score += 10
        
        if abs(macd_val - macd_sig) > 0: score += 20

        # Signal Logic
        signal = "NEUTRAL ⏸️"
        sl, tp1, tp2 = 0.0, 0.0, 0.0
        
        if price > vwap and ema20 > ema50 and macd_val > macd_sig and rsi < 65 and vol_ratio >= 0.8 and score >= 60:
            signal = "STRONG BUY 🚀"
            sl = price - (atr * 1.5)
            tp1 = price + (atr * 2.0)
            tp2 = price + (atr * 3.5)
        elif price < vwap and ema20 < ema50 and macd_val < macd_sig and rsi > 35 and vol_ratio >= 0.8 and score >= 60:
            signal = "STRONG SELL 💥"
            sl = price + (atr * 1.5)
            tp1 = price - (atr * 2.0)
            tp2 = price - (atr * 3.5)
            
        return {
            'df': df, 'symbol': ticker_clean, 'price': price, 'signal': signal, 
            'score': score, 'vwap': vwap, 'ema20': ema20, 'ema50': ema50,
            'rsi': rsi, 'atr': atr, 'vol_ratio': vol_ratio, 'sl': sl, 'tp1': tp1, 'tp2': tp2
        }
    except Exception as e:
        return None

# Navigation / Tabs
tab1, tab2 = st.tabs(["🎯 Single Stock Terminal & Chart", "🔥 Multi-Stock Auto Scanner"])

with st.sidebar:
    st.header("⚙️ Scanner Control Panel")
    selected_tf = st.selectbox("⏱️ Timeframe", ["5m", "15m", "1h"], index=1)
    st.markdown("---")
    st.subheader("💰 Capital & Risk Sizer")
    capital = st.number_input("Total Capital (₹)", value=50000, step=5000)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 3.0, 1.0, 0.5)

# --- TAB 1: SINGLE STOCK TERMINAL & CHART ---
with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        stock_input = st.text_input("Enter NSE Stock Symbol", "TATAMOTORS")
        analyze_btn = st.button("⚡ ANALYZE STOCK")
    
    if stock_input:
        res = analyze_stock(stock_input, selected_tf)
        if res is None:
            st.error("❌ Invalid Stock Symbol or Data Unavailable! (Try during market hours or change timeframe)")
        else:
            df = res['df']
            p, r1, s1, r2, s2 = calculate_pivots(df)
            
            # Key Metrics Display
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Live Price", f"₹{res['price']:.2f}")
            m2.metric("Signal", res['signal'])
            m3.metric("Health Score", f"{res['score']}/100")
            m4.metric("Volume Ratio", f"{res['vol_ratio']:.2f}x")
            
            # Risk Sizer Calculation
            risk_amount = capital * (risk_pct / 100)
            sl_dist = abs(res['price'] - res['sl']) if res['sl'] > 0 else res['atr'] * 1.5
            qty = int(risk_amount / sl_dist) if sl_dist > 0 else 0
            trade_val = qty * res['price']
            
            st.markdown("---")
            col_left, col_right = st.columns([1.2, 1])
            
            with col_left:
                st.subheader("🎯 Trade Levels & Risk Management")
                t1, t2, t3 = st.columns(3)
                t1.metric("Stop Loss (SL)", f"₹{res['sl']:.2f}" if res['sl']>0 else "N/A")
                t2.metric("Target 1 (Safe)", f"₹{res['tp1']:.2f}" if res['tp1']>0 else "N/A")
                t3.metric("Target 2 (Max)", f"₹{res['tp2']:.2f}" if res['tp2']>0 else "N/A")
                
                st.info(f"""
                💡 **Position Sizing Calculator:**
                - **Recommended Quantity:** {qty} Shares
                - **Trade Value:** ₹{trade_val:,.2f}
                - **Max Risk Amount:** ₹{risk_amount:,.2f} (at {risk_pct}% risk)
                """)
                
                st.markdown("##### 📌 Pivot Levels (Support & Resistance)")
                pv1, pv2, pv3, pv4 = st.columns(4)
                pv1.metric("Resistance 2", f"₹{r2:.2f}")
                pv2.metric("Resistance 1", f"₹{r1:.2f}")
                pv3.metric("Support 1", f"₹{s1:.2f}")
                pv4.metric("Support 2", f"₹{s2:.2f}")

            with col_right:
                st.subheader("🔍 Technical Confluence Check")
                st.write(f"• **VWAP Line:** ₹{res['vwap']:.2f} ({'Price Above 📈' if res['price']>res['vwap'] else 'Price Below 📉'})")
                st.write(f"• **EMA Trend (20/50):** {'Bullish Crossover 🟢' if res['ema20']>res['ema50'] else 'Bearish Crossover 🔴'}")
                st.write(f"• **RSI Indicator:** {res['rsi']:.1f} ({'Neutral Momentum' if 40<=res['rsi']<=60 else 'Overbought/Oversold'})")
                st.write(f"• **Volatility (ATR):** ₹{res['atr']:.2f}")

            # Plotly Interactive Chart
            st.subheader("📈 Interactive Candlestick & Technical Chart")
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
            
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='yellow', width=1.5), name="EMA 20"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='cyan', width=1.5), name="EMA 50"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='magenta', width=2), name="VWAP"), row=1, col=1)
            
            colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red' for i in range(len(df))]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
            
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: MULTI-STOCK AUTO SCANNER ---
with tab2:
    st.subheader("🔥 Top Nifty Intraday Watchlist Scanner")
    st.write("Click below to scan top high-liquidity stocks instantly for institutional setups.")
    
    if st.button("🚀 RUN FULL WATCHLIST SCANNER"):
        results = []
        progress_bar = st.progress(0)
        
        for idx, stock in enumerate(WATCHLIST):
            r = analyze_stock(stock, selected_tf)
            if r:
                results.append({
                    "Stock": r['symbol'],
                    "Signal": r['signal'],
                    "Health Score": r['score'],
                    "Price (₹)": f"₹{r['price']:.2f}",
                    "Vol Ratio": f"{r['vol_ratio']:.2f}x",
                    "RSI": f"{r['rsi']:.1f}",
                    "SL (₹)": f"₹{r['sl']:.2f}" if r['sl']>0 else "-",
                    "Target 1 (₹)": f"₹{r['tp1']:.2f}" if r['tp1']>0 else "-"
                })
            progress_bar.progress((idx + 1) / len(WATCHLIST))
            
        scan_df = pd.DataFrame(results)
        
        def color_signals(val):
            if "BUY" in str(val): return 'background-color: #1b4332; color: #52b788; font-weight: bold;'
            if "SELL" in str(val): return 'background-color: #49111c; color: #ff4d6d; font-weight: bold;'
            return ''
            
        st.dataframe(scan_df.style.map(color_signals, subset=['Signal']), use_container_width=True)
        
