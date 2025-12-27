# services/relative.py
import pandas as pd
import numpy as np

def build_peer_table(target_ticker: str, peer_infos: dict) -> pd.DataFrame:
    """
    peer_infos: { "BBRI.JK": info_dict, ... }
    """
    rows = []
    for tkr, info in peer_infos.items():
        rows.append({
            "Ticker": tkr,
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "PE": info.get("trailingPE"),
            "PBV": info.get("priceToBook"),
            "ROE%": (info.get("returnOnEquity") or np.nan) * 100,
            "MCap": info.get("marketCap"),
        })

    df = pd.DataFrame(rows)

    # buang baris yang benar2 kosong
    df = df.dropna(subset=["PE", "PBV", "ROE%"], how="all")
    return df

def calc_relative_snapshot(target_info: dict, peer_df: pd.DataFrame) -> dict:
    """
    Output: target vs median peers (best effort)
    """
    med = peer_df.median(numeric_only=True) if peer_df is not None and not peer_df.empty else pd.Series(dtype=float)

    t_pe = target_info.get("trailingPE")
    t_pbv = target_info.get("priceToBook")
    t_roe = (target_info.get("returnOnEquity") or None)
    t_roe = (t_roe * 100) if t_roe is not None else None

    return {
        "target": {"PE": t_pe, "PBV": t_pbv, "ROE%": t_roe},
        "median": {
            "PE": float(med["PE"]) if "PE" in med else None,
            "PBV": float(med["PBV"]) if "PBV" in med else None,
            "ROE%": float(med["ROE%"]) if "ROE%" in med else None,
        }
    }

def label_relative(value, median, band=0.15):
    """
    band 15%: < median*(1-band) => DISKON, > median*(1+band) => MAHAL
    """
    if value is None or median is None or median == 0:
        return "N/A"
    if value < median * (1 - band):
        return "DISKON"
    if value > median * (1 + band):
        return "MAHAL"
    return "FAIR"
