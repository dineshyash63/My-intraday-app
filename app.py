import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="AI Intraday Pro Hub", layout="wide")

st.title("👑 AI Intraday Pro Scanner Hub (Ultimate Edition)")
st.caption("Live Multi-Indicator Confluence, Health Score & Risk Management Calculator")

col1, col2 = st.columns([1, 2])

with col1:
    ticker = st.text_input("🎯 Stock Symbol (e.g. TATAMOTORS, RELIANCE, SBIN)", "TATAMOTORS")
    timeframe = st.selectbox("⏱️ Timeframe", ["5m", "15m", "1h"], index=1)
    scan_btn = st.button("🔍 SCAN STOCK NOW", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📌 Top Daily Stocks:")
    st.markdown("- **Banking:** SBIN, ICICIBANK, AXISBANK")
    st.markdown("- **Auto & Tech:** TATAMOTORS, M&M, INFY")
    st.markdown("- **Energy:** RELIANCE, TATASTEEL")

if scan_btn or ticker:
    try:
        ticker_clean = ticker.strip().upper()
        ticker_ns = ticker_clean + ".NS" if not ticker_clean.endswith(".NS") else ticker_clean
        
        df = yf.download(ticker_ns, period="5d", interval=timeframe, progress=False)
        
        if df.empty or len(df) < 50:
            st.error("❌ Data பெற முடியவில்லை! Ticker-ஐ சரிபார்க்கவும்.")
        else:
            close = df['Close'].squeeze()
            high = df['High'].squeeze()
            low = df['Low'].squeeze()
            volume = df['Volume'].squeeze()
            
            rsi = float(ta.momentum.rsi(close, window=14).iloc[-1])
            atr = float(ta.volatility.average_true_range(high, low, close, window=14).iloc[-1])
            ema20 = float(ta.trend.ema_indicator(close, window=20).iloc[-1])
            ema50 = float(ta.trend.ema_indicator(close, window=50).iloc[-1])
            
            macd_obj = ta.trend.MACD(close)
            macd_val = float(macd_obj.macd().iloc[-1])
            macd_sig = float(macd_obj.macd_signal().iloc[-1])
            
            price = float(close.iloc[-1])
            curr_vol = float(volume.iloc[-1])
            avg_vol = float(ta.trend.sma_indicator(volume, window=20).iloc[-1])
            
            vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0
            score = 0
            if vol_ratio >= 1.2: score += 30
            elif vol_ratio >= 0.8: score += 15
            if (atr / price) * 100 >= 0.7: score += 30
            elif (atr / price) * 100 >= 0.4: score += 15
            if abs(ema20 - ema50) / price > 0.002: score += 20
            if 40 <= rsi <= 60 or rsi < 30 or rsi > 70: score += 20
            
            signal = "⏸️ NEUTRAL / WAIT"
            sl, tp1, tp2 = "N/A", "N/A", "N/A"
            
            if ema20 > ema50 and macd_val > macd_sig and rsi < 48 and vol_ratio >= 0.9:
                signal = "🚀 ULTRA STRONG BUY"
                sl = f"₹{price - (atr * 1.3):.2f}"
                tp1 = f"₹{price + (atr * 2.0):.2f}"
                tp2 = f"₹{price + (atr * 3.5):.2f}"
            elif ema20 < ema50 and macd_val < macd_sig and rsi > 52 and vol_ratio >= 0.9:
                signal = "💥 ULTRA STRONG SELL"
                sl = f"₹{price + (atr * 1.3):.2f}"
                tp1 = f"₹{price - (atr * 2.0):.2f}"
                tp2 = f"₹{price - (atr * 3.5):.2f}"

            with col2:
                m1, m2 = st.columns(2)
                m1.metric("Current Price", f"₹{price:.2f}")
                m2.metric("Action Signal", signal)
                
                st.info(f"📊 **Intraday Health Score:** {score}/100 | Volume: {vol_ratio:.1f}x Avg")
                
                if ema20 > ema50 and macd_val > macd_sig:
                    st.success("📈 Market Regime: STRONG UPTREND")
                elif ema20 < ema50 and macd_val < macd_sig:
                    st.error("📉 Market Regime: STRONG DOWNTREND")
                else:
                    st.warning("🔄 Market Regime: SIDEWAYS / CHOPPY")
                    
                t1, t2, t3 = st.columns(3)
                t1.metric("Stop-Loss (SL)", sl)
                t2.metric("Target 1 (Safe)", tp1)
                t3.metric("Target 2 (Max)", tp2)

    except Exception as e:
        st.error(f"Error: {str(e)}")
  
