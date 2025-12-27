import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)
@st.cache_data(ttl=300, show_spinner=False)
def get_ohlcv(ticker: str, period="2y", interval="1d") -> pd.DataFrame:
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            group_by="column",   # PENTING
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # ===== FIX MULTIINDEX =====
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        # ===== VALIDASI KETAT =====
        required = {"Open", "High", "Low", "Close", "Volume"}
        if not required.issubset(set(df.columns)):
            return pd.DataFrame()

        return df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_info(ticker: str) -> dict:
    return yf.Ticker(ticker).info or {}

@st.cache_data(ttl=3600)
def get_financials(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    # Yahoo kadang tidak lengkap; kita ambil yang ada
    return {
        "income": t.income_stmt,          # annual
        "balance": t.balance_sheet,       # annual
        "cashflow": t.cashflow,           # annual
        "income_q": t.quarterly_income_stmt,
        "cashflow_q": t.quarterly_cashflow,
    }
