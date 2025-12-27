import pandas as pd

def summarize_annual(fin: pd.DataFrame, keys: list[str], years=5) -> pd.DataFrame:
    if fin is None or fin.empty:
        return pd.DataFrame()

    df = fin.copy()

    # 1️⃣ pastikan kolom datetime
    df.columns = pd.to_datetime(df.columns, errors="coerce")

    # 2️⃣ urutkan dari tahun TERBARU ke LAMA
    df = df.sort_index(axis=1, ascending=False)

    # 3️⃣ ambil N tahun terakhir
    cols = df.columns[:years]

    # 4️⃣ filter hanya metric yang ada
    valid_keys = [k for k in keys if k in df.index]
    if not valid_keys:
        return pd.DataFrame()

    out = df.loc[valid_keys, cols]

    # 5️⃣ rename kolom jadi tahun saja (string)
    out.columns = [str(c.year) for c in out.columns]

    out.index.name = "Metric"
    return out


def key_financial_tables(fin_data: dict):
    income = fin_data.get("income")
    balance = fin_data.get("balance")
    cashflow = fin_data.get("cashflow")

    income_keys = [
        "Total Revenue",
        "Gross Profit",
        "Operating Income",
        "EBIT",
        "EBITDA",
        "Net Income",
    ]

    balance_keys = [
        "Total Assets",
        "Total Liab",
        "Total Stockholder Equity",
        "Cash And Cash Equivalents",
        "Short Long Term Debt",
        "Long Term Debt",
    ]

    cashflow_keys = [
        "Total Cash From Operating Activities",
        "Capital Expenditures",
        "Free Cash Flow",
    ]

    return {
        "income": summarize_annual(income, income_keys),
        "balance": summarize_annual(balance, balance_keys),
        "cashflow": summarize_annual(cashflow, cashflow_keys),
    }
