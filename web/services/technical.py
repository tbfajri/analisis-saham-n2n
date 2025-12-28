import pandas as pd
import numpy as np

def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean().replace(0, 1e-12)
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    if "Close" not in df.columns:
        return pd.DataFrame()

    d = df.copy()
    d["EMA20"] = ema(d["Close"], 20)
    d["EMA50"] = ema(d["Close"], 50)
    d["EMA200"] = ema(d["Close"], 200)
    d["RSI14"] = rsi(d["Close"], 14)
    d["ATR14"] = atr(d, 14)
    d["VOL_AVG20"] = d["Volume"].rolling(20).mean()
    return d


def technical_plan(df: pd.DataFrame, rr=2.0, pullback_pct=0.03, atr_mult=1.2):
    last = df.iloc[-1]

    close = float(last["Close"])
    ema20 = float(last["EMA20"])
    ema50 = float(last["EMA50"])
    ema200 = float(last["EMA200"])
    rsi14 = float(last["RSI14"])
    atr14 = float(last["ATR14"])
    vol = float(last["Volume"])
    vol_avg = float(last["VOL_AVG20"]) if float(last["VOL_AVG20"]) > 0 else 1.0
    vol_ratio = vol / vol_avg

    # ---- Trend
    trend = "SIDEWAYS"
    if ema20 > ema50 > ema200:
        trend = "UPTREND"
    elif ema20 < ema50 < ema200:
        trend = "DOWNTREND"

    # ---- Pullback (ke EMA20)
    pullback_ok = abs(close - ema20) / ema20 <= pullback_pct

    # ---- RSI context (lebih fleksibel)
    rsi_ok = 45 <= rsi14 <= 70 if trend == "UPTREND" else 40 <= rsi14 <= 60

    # ---- Volume confirmation
    vol_ok = vol_ratio >= 1.2

    # ---- Entry (defensif)
    entry_low = ema20 * 0.995
    entry_high = ema20 * 1.005
    entry = (entry_low + entry_high) / 2

    # ---- Stoploss (logis, bukan dipaksa)
    sl_ema = ema50 * 0.985
    sl_atr = entry - atr_mult * atr14
    stop = min(sl_ema, sl_atr)  # beri ruang napas

    # ---- Risk check
    risk = entry - stop
    if risk <= 0:
        return {
            "setup_ok": False,
            "reason": "Invalid risk (entry <= stop)"
        }

    # ---- Take profit
    tp = entry + rr * risk

    setup_ok = (
        trend == "UPTREND"
        and pullback_ok
        and rsi_ok
        and vol_ok
    )

    return {
        "close": close,
        "trend": trend,
        "rsi14": rsi14,
        "vol_ratio": round(vol_ratio, 2),
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry": entry,
        "stop": stop,
        "tp": tp,
        "rr": rr,
        "setup_ok": setup_ok
    }
