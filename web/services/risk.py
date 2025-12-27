# services/risk.py
def risk_flags(info: dict, tables: dict) -> list[str]:
    risks = []

    # Valuasi / profitabilitas sederhana (best effort)
    roe = info.get("returnOnEquity")
    if roe is not None and roe < 0.10:
        risks.append("🟡 ROE rendah (<10%)")

    debt_to_equity = info.get("debtToEquity")
    if debt_to_equity is not None and debt_to_equity > 150:
        # Yahoo kadang pakai persen (150 = 150%)
        risks.append("🟠 Debt-to-Equity tinggi")

    # Cashflow red flag
    cf = tables.get("cashflow")
    if cf is not None and not cf.empty and "Free Cash Flow" in cf.index:
        fcf = cf.loc["Free Cash Flow"]
        if (fcf < 0).any():
            risks.append("🟠 Free Cash Flow pernah negatif (salah satu tahun)")

    # Income consistency (net income drop)
    inc = tables.get("income")
    if inc is not None and not inc.empty and "Net Income" in inc.index:
        ni = inc.loc["Net Income"]
        if len(ni) >= 2 and (ni.iloc[-1] < ni.iloc[-2]):
            risks.append("🟡 Net Income terakhir turun vs tahun sebelumnya")

    # Market cap kecil (opsional)
    mcap = info.get("marketCap") or 0
    if mcap and mcap < 2e12:
        risks.append("🟡 Market cap kecil (lebih volatile / risk tinggi)")

    return risks
