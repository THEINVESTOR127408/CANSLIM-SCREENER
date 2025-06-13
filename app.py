import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="CANSLIM Stock Screener", layout="wide")

st.title("📈 CANSLIM Stock Screener (Yahoo Finance)")

# --- Filters ---
with st.sidebar:
    st.header("📊 Filter Criteria")
    min_eps_growth = st.number_input("Min EPS Growth (Quarterly YoY %)", 0, 500, 25)
    min_annual_growth = st.number_input("Min Annual EPS Growth (%)", 0, 500, 15)
    max_pe = st.number_input("Max P/E Ratio", 0, 500, 40)
    min_price = st.number_input("Min Stock Price", 0, 10000, 10)
    max_price = st.number_input("Max Stock Price", 0, 10000, 500)
    only_near_highs = st.checkbox("Only Near 52-Week Highs", value=True)
    symbols = st.text_area("Tickers (comma-separated)", "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META").split(",")

# --- Load & Screen ---
def fetch_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        hist = stock.history(period="1y")
        current_price = hist["Close"][-1]
        high_52wk = hist["Close"].max()

        eps_growth = info.get("earningsQuarterlyGrowth", None)
        annual_growth = info.get("earningsGrowth", None)
        pe_ratio = info.get("trailingPE", None)

        return {
            "Ticker": ticker.upper(),
            "Price": current_price,
            "52W High": high_52wk,
            "EPS QoQ Growth %": eps_growth * 100 if eps_growth else None,
            "Annual EPS Growth %": annual_growth * 100 if annual_growth else None,
            "P/E": pe_ratio,
            "Near High": (current_price / high_52wk) > 0.9 if high_52wk else False,
        }
    except:
        return None

st.subheader("📃 Results")
results = []
with st.spinner("Fetching stock data..."):
    for symbol in symbols:
        symbol = symbol.strip().upper()
        data = fetch_data(symbol)
        if data:
            results.append(data)

df = pd.DataFrame(results)

# --- Apply Filters ---
if not df.empty:
    df = df[df["Price"].between(min_price, max_price)]
    df = df[df["EPS QoQ Growth %"] >= min_eps_growth]
    df = df[df["Annual EPS Growth %"] >= min_annual_growth]
    df = df[df["P/E"] <= max_pe]
    if only_near_highs:
        df = df[df["Near High"] == True]

    st.dataframe(df.sort_values(by="EPS QoQ Growth %", ascending=False), use_container_width=True)
else:
    st.warning("No data returned. Check ticker list or filters.")
