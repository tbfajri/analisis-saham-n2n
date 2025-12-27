import pandas as pd
import numpy as np

def obv(df: pd.DataFrame) -> pd.Series:
    direction = np.sign(df["Close"].diff()).fillna(0)
    return (direction * df["Volume"]).cumsum()

def adl(df: pd.DataFrame) -> pd.Series:
    high, low, close, vol = df["High"], df["Low"], df["Close"], df["Volume"]
    mfm = ((close - low) - (high - close)) / (high - low).replace(0, 1e-12)
    mfv = mfm * vol
    return mfv.cumsum()

def orderflow_radar(df: pd.DataFrame, lookback=20):
    d = df.copy()
    d["OBV"] = obv(d)
    d["ADL"] = adl(d)
    d["VOL_AVG20"] = d["Volume"].rolling(20).mean()

    recent = d.tail(lookback)
    obv_slope = recent["OBV"].iloc[-1] - recent["OBV"].iloc[0]
    adl_slope = recent["ADL"].iloc[-1] - recent["ADL"].iloc[0]

    # volume anomaly + candle strength
    last = d.iloc[-1]
    vol_ratio = float(last["Volume"]) / (float(last["VOL_AVG20"]) if float(last["VOL_AVG20"]) > 0 else 1.0)
    rng = float(last["High"] - last["Low"]) if float(last["High"] - last["Low"]) != 0 else 1.0
    close_pos = float((last["Close"] - last["Low"]) / rng)  # 0..1, >0.7 close near high

    # simple label
    if obv_slope > 0 and adl_slope > 0 and vol_ratio >= 1.5 and close_pos >= 0.6:
        label = "AKUMULASI"
    elif obv_slope < 0 and adl_slope < 0 and vol_ratio >= 1.5 and close_pos <= 0.4:
        label = "DISTRIBUSI"
    else:
        label = "NETRAL"

    return {
        "label": label,
        "vol_ratio": vol_ratio,
        "close_pos": close_pos,
        "obv_slope": obv_slope,
        "adl_slope": adl_slope,
        "obv_series": d["OBV"],
        "adl_series": d["ADL"],
    }
