import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from services.data import get_ohlcv, get_info, get_financials
from services.news import google_news_rss
from services.technical import add_indicators, technical_plan
from services.orderflow import orderflow_radar
from services.financials import key_financial_tables
from services.valuation import fair_value_pe, fair_value_pbv, classify_valuation
from services.scoring import score_all, verdict
from services.relative import build_peer_table, calc_relative_snapshot, label_relative
from services.risk import risk_flags
from services.fundamental_score import fundamental_score
from services.verdict_engine import final_verdict


from utils import rupiah, rupiah_short


st.set_page_config(page_title="StockLab", layout="wide")

def load_watchlist(path="watchlist.txt"):
    try:
        with open(path, "r") as f:
            tickers = []
            for line in f:
                t = line.strip().upper()
                if not t:
                    continue

                # kalau belum ada suffix .JK → tambahin
                if not t.endswith(".JK"):
                    t = f"{t}.JK"

                tickers.append(t)

            return tickers

    except FileNotFoundError:
        return ["BBRI.JK", "ADRO.JK"]


def candle_chart(df, title):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA20", mode="lines"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], name="EMA50", mode="lines"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], name="EMA200", mode="lines"))
    fig.update_layout(height=520, title=title, xaxis_rangeslider_visible=False)
    return fig

def format_fin_table(df):
    if df is None or df.empty:
        return df

    f = df.copy()
    for c in f.columns:
        f[c] = f[c].apply(rupiah_short)
    return f

def trend_label(series):
    if series is None or len(series) < 2:
        return "N/A"
    try:
        return "📈 Growing" if series.iloc[-1] > series.iloc[0] else ("📉 Declining" if series.iloc[-1] < series.iloc[0] else "➖ Flat")
    except Exception:
        return "N/A"


st.title("📈 StockLab — Analisis Saham End-to-End")

watchlist = load_watchlist()

with st.sidebar:
    ticker = st.selectbox("Pilih saham", watchlist, index=0)
    period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=2)
    rr = st.slider("Risk:Reward", 1.5, 3.0, 2.0, 0.5)

    st.divider()
    st.subheader("Valuation Assumption")
    target_pe = st.number_input("Target PE", min_value=1.0, value=12.0, step=1.0)
    target_pbv = st.number_input("Target PBV", min_value=0.1, value=2.0, step=0.1)

df_raw = get_ohlcv(ticker, period=period, interval="1d")
min_bars = 220 if period in ["2y", "5y"] else 120

if df_raw.empty or len(df_raw) < min_bars:
    st.warning(
        f"Data OHLCV terbatas ({len(df_raw)} bar). "
        "Analisis disederhanakan (EMA200 / bandarmologi bisa kurang akurat)."
    )

df = add_indicators(df_raw)

info = get_info(ticker)
fin = get_financials(ticker)
# --- Peer infos (best effort, dari watchlist)
peer_infos = {ticker: info}  


# ---- 1) Profile
st.header("1) Profil Perusahaan")
col1, col2, col3 = st.columns([1.2, 1, 1])
with col1:
    st.write({
        "Ticker": ticker,
        "Name": info.get("longName") or info.get("shortName"),
        "Sector": info.get("sector"),
        "Industry": info.get("industry"),
        "Website": info.get("website"),
        "Market Cap": rupiah_short(info.get("marketCap")),
    })
with col2:
    st.write("**Description**")
    st.caption((info.get("longBusinessSummary") or "")[:600] + ("..." if info.get("longBusinessSummary") else ""))
with col3:
    last_close = float(df["Close"].iloc[-1])
    st.metric("Last Close", f"{last_close:,.2f}")
    st.metric("52W High", f"{float(df['High'].tail(252).max()):,.2f}")
    st.metric("52W Low", f"{float(df['Low'].tail(252).min()):,.2f}")

# ---- 2) News
st.header("2) Berita Terkait")
q = f"{ticker.replace('.JK','')} saham"
news = google_news_rss(q, max_items=10)
if not news:
    st.info("Belum dapat berita dari RSS. Coba query lain atau cek koneksi.")
else:
    st.subheader("Berita Terkait")
    for n in news:
        st.markdown(
            f"- **[{n['title']}]({n['link']})**  \n"
            f"  <small>{n.get('source','')} • {n.get('published','')}</small>",
            unsafe_allow_html=True
        )


# ---- 3) Financials 5Y
st.header("3) Statistik Keuangan (Best-effort 5 Tahun)")
tables = key_financial_tables(fin)

cA, cB, cC = st.columns(3)

with cA:
    st.subheader("Income")
    st.dataframe(
        format_fin_table(tables["income"])
        if not tables["income"].empty else pd.DataFrame({"info": ["No data"]}),
        use_container_width=True
    )

with cB:
    st.subheader("Balance Sheet")
    st.dataframe(
        format_fin_table(tables["balance"])
        if not tables["balance"].empty else pd.DataFrame({"info": ["No data"]}),
        use_container_width=True
    )

with cC:
    st.subheader("Cashflow")
    st.dataframe(
        format_fin_table(tables["cashflow"])
        if not tables["cashflow"].empty else pd.DataFrame({"info": ["No data"]}),
        use_container_width=True
    )

st.header("📐 Key Ratios (Derived)")

def safe_div(a, b):
    return (a / b) if (a is not None and b not in (None, 0)) else None

def yoy_growth(series):
    if series is None or len(series) < 2:
        return None
    return (series.iloc[0] - series.iloc[1]) / abs(series.iloc[1]) * 100

# ---- layout ke samping
c1, c2, c3 = st.columns(3)

if not tables["income"].empty:
    inc = tables["income"]

    # Gross Margin
    with c1:
        if "Gross Profit" in inc.index and "Total Revenue" in inc.index:
            gm = safe_div(inc.loc["Gross Profit"].iloc[0], inc.loc["Total Revenue"].iloc[0])
            st.metric("Gross Margin", f"{gm*100:.1f}%" if gm is not None else "-")
        else:
            st.metric("Gross Margin", "-")

    # Net Margin
    with c2:
        if "Net Income" in inc.index and "Total Revenue" in inc.index:
            nm = safe_div(inc.loc["Net Income"].iloc[0], inc.loc["Total Revenue"].iloc[0])
            st.metric("Net Margin", f"{nm*100:.1f}%" if nm is not None else "-")
        else:
            st.metric("Net Margin", "-")

    # Revenue YoY
    with c3:
        if "Total Revenue" in inc.index:
            rev = inc.loc["Total Revenue"]
            g = yoy_growth(rev)
            st.metric("Revenue YoY", f"{g:.1f}%" if g is not None else "-")
        else:
            st.metric("Revenue YoY", "-")


rev_yoy = None
ni_yoy = None

if not tables["income"].empty:
    inc = tables["income"]
    if "Total Revenue" in inc.index and len(inc.loc["Total Revenue"]) >= 2:
        s = inc.loc["Total Revenue"]
        rev_yoy = (s.iloc[0] - s.iloc[1]) / abs(s.iloc[1]) * 100 if s.iloc[1] != 0 else None

    if "Net Income" in inc.index and len(inc.loc["Net Income"]) >= 2:
        s = inc.loc["Net Income"]
        ni_yoy = (s.iloc[0] - s.iloc[1]) / abs(s.iloc[1]) * 100 if s.iloc[1] != 0 else None

gross_margin = None
net_margin = None
if not tables["income"].empty:
    inc = tables["income"]
    if "Gross Profit" in inc.index and "Total Revenue" in inc.index:
        gross_margin = inc.loc["Gross Profit"].iloc[0] / inc.loc["Total Revenue"].iloc[0]
    if "Net Income" in inc.index and "Total Revenue" in inc.index:
        net_margin = inc.loc["Net Income"].iloc[0] / inc.loc["Total Revenue"].iloc[0]

roe = info.get("returnOnEquity")
roe = roe * 100 if roe is not None else None

de_ratio = info.get("debtToEquity")
equity_ratio = None
if not tables["balance"].empty:
    bal = tables["balance"]
    if "Total Stockholder Equity" in bal.index and "Total Assets" in bal.index:
        equity_ratio = bal.loc["Total Stockholder Equity"].iloc[0] / bal.loc["Total Assets"].iloc[0]

fcf_series = None
if not tables["cashflow"].empty and "Free Cash Flow" in tables["cashflow"].index:
    fcf_series = tables["cashflow"].loc["Free Cash Flow"]

result = fundamental_score({
    "rev_yoy": rev_yoy,
    "ni_yoy": ni_yoy,
    "gross_margin": gross_margin,
    "net_margin": net_margin,
    "roe": roe,
    "de_ratio": de_ratio,
    "equity_ratio": equity_ratio,
    "fcf_series": fcf_series
})


st.header("🧮 Fundamental Scoring")

c1, c2 = st.columns([1, 2])
with c1:
    st.metric("Fundamental Score", f"{result['score']}/100")
    st.metric("Grade", result["grade"])

with c2:
    st.subheader("Alasan Utama")
    for r in result["reasons"][:6]:
        st.write(f"- {r}")


st.header("📊 Relative Analysis (vs Peer Watchlist)")

peer_df = build_peer_table(ticker, peer_infos)

# filter peers yang satu sektor (kalau tersedia)
target_sector = info.get("sector")
peer_same_sector = peer_df[peer_df["Sector"] == target_sector] if target_sector and not peer_df.empty else peer_df

snap = calc_relative_snapshot(info, peer_same_sector)

c1, c2, c3 = st.columns(3)

pe_label = label_relative(snap["target"]["PE"], snap["median"]["PE"])
pbv_label = label_relative(snap["target"]["PBV"], snap["median"]["PBV"])
roe_label = label_relative(snap["target"]["ROE%"], snap["median"]["ROE%"], band=0.20)

with c1:
    st.metric("PE (target)", f"{snap['target']['PE']:.2f}" if snap["target"]["PE"] else "-")
    st.caption(f"Peer median: {snap['median']['PE']:.2f}" if snap["median"]["PE"] else "Peer median: -")
    st.write(f"Label: **{pe_label}**")

with c2:
    st.metric("PBV (target)", f"{snap['target']['PBV']:.2f}" if snap["target"]["PBV"] else "-")
    st.caption(f"Peer median: {snap['median']['PBV']:.2f}" if snap["median"]["PBV"] else "Peer median: -")
    st.write(f"Label: **{pbv_label}**")

with c3:
    st.metric("ROE% (target)", f"{snap['target']['ROE%']:.1f}%" if snap["target"]["ROE%"] else "-")
    st.caption(f"Peer median: {snap['median']['ROE%']:.1f}%" if snap["median"]["ROE%"] else "Peer median: -")
    st.write(f"Label: **{roe_label}**")

with st.expander("Lihat tabel peer"):
    st.dataframe(peer_same_sector.sort_values(by="MCap", ascending=False), use_container_width=True)

# ---- Key Risks
st.header("⚠️ Key Risks (Red Flags)")

risks = risk_flags(info, tables)

if not risks:
    st.success("Tidak ada red flag utama terdeteksi dari data yang tersedia.")
else:
    for r in risks:
        st.warning(r)

# ---- 4) Valuation
st.header("4️) Nilai Wajar vs Harga Terbaru")

last_price = last_close  # sudah kamu hitung sebelumnya

eps = info.get("trailingEps")
bvps = info.get("bookValue")

fv_pe = fair_value_pe(eps, target_pe) if eps else None
fv_pbv = fair_value_pbv(bvps, target_pbv) if bvps else None

# combine fair value (rata-rata yang available)
vals = [v for v in [fv_pe, fv_pbv] if v is not None and v > 0]
fair = sum(vals) / len(vals) if vals else None

# diskon / premium vs fair value
discount_pct = None
if fair and fair > 0:
    discount_pct = (fair - last_price) / fair * 100

label = classify_valuation(last_price, fair, band=0.10) if fair else "UNKNOWN"

# =========================
# DISPLAY (HORIZONTAL KPI)
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Harga Terbaru", rupiah(last_price, 0))

with c2:
    st.metric("Fair Value (PE)", rupiah(fv_pe, 0) if fv_pe else "-")

with c3:
    st.metric("Fair Value (PBV)", rupiah(fv_pbv, 0) if fv_pbv else "-")

with c4:
    st.metric("Fair Value (Combined)", rupiah(fair, 0) if fair else "-")

# =========================
# DISKON / PREMIUM
# =========================
if discount_pct is not None:
    if discount_pct > 0:
        st.success(f"📉 Diskon terhadap fair value: {discount_pct:.1f}%")
    else:
        st.error(f"📈 Premium terhadap fair value: {abs(discount_pct):.1f}%")

# =========================
# SUMMARY TABLE
# =========================
st.write({
    "Harga Terbaru": rupiah(last_price, 0),
    "Trailing EPS": eps,
    "Book Value/Share": rupiah(bvps, 0) if bvps else None,
    "Fair Value (PE)": rupiah(fv_pe, 0) if fv_pe else None,
    "Fair Value (PBV)": rupiah(fv_pbv, 0) if fv_pbv else None,
    "Fair Value (Combined)": rupiah(fair, 0) if fair else None,
    "Diskon / Premium (%)": f"{discount_pct:.1f}%" if discount_pct is not None else None,
    "Valuation": label,
})

# ---- 5) Technical plan
st.header("5) Teknikal: Entry, Cutloss, TP (RR 1:2)")
plan = technical_plan(df, rr=rr)
st.write({
    "Trend": plan["trend"],
    "RSI14": round(plan["rsi14"], 2),
    "Volume Ratio": round(plan["vol_ratio"], 2),
    "Setup Valid": plan["setup_ok"],
    "Entry Low": rupiah(plan["entry_low"], 0),
    "Entry High": rupiah(plan["entry_high"], 0),
    "Stoploss": rupiah(plan["stop"], 0),
    "Take Profit": rupiah(plan["tp"], 0),
})

st.plotly_chart(candle_chart(df, f"{ticker} | {period}"), use_container_width=True)

# ---- 6) Bandarmologi proxy
st.header("6) Bandarmologi (Radar Akumulasi/Distribusi)")
rad = orderflow_radar(df, lookback=20)
st.write({
    "Radar": rad["label"],
    "Vol Ratio": round(rad["vol_ratio"], 2),
    "Close Position": round(rad["close_pos"], 2),
})

# ---- 7) FINAL SUMMARY & VERDICT
st.header("7️⃣ Final Verdict: BUY / HOLD / SELL")

# =========================
# FINAL VERDICT ENGINE
# =========================
final = final_verdict(
    fundamental_score=result["score"],
    valuation_label=label,
    technical_ok=plan["setup_ok"],
    bandarmologi_label=rad["label"],
)

# =========================
# KPI DISPLAY
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Fundamental Score", f"{result['score']}/100")
    st.caption(f"Grade: {result['grade']}")

with c2:
    st.metric("Valuation", label)

with c3:
    st.metric("Technical Setup", "VALID" if plan["setup_ok"] else "NOT READY")

with c4:
    st.metric("Verdict", final["verdict"])
    st.caption(f"Confidence: {final['confidence']}")

# =========================
# VISUAL STATUS
# =========================
if final["verdict"].startswith("BUY"):
    st.success(f"✅ {final['verdict']} — Confidence {final['confidence']}")
elif "HOLD" in final["verdict"]:
    st.warning(f"⏸️ {final['verdict']} — Confidence {final['confidence']}")
else:
    st.error(f"❌ {final['verdict']} — Confidence {final['confidence']}")

# =========================
# DECISION RATIONALE
# =========================
st.subheader("🧠 Decision Rationale")

# Fundamental reasons
for r in final["reasons"]:
    st.write(f"- {r}")

# Technical context
if plan["setup_ok"]:
    st.write("- Setup teknikal valid (trend + pullback + momentum).")
else:
    st.write("- Setup teknikal belum valid (tunggu pullback / konfirmasi).")

# Valuation context
if label == "DISKON":
    st.write("- Valuasi relatif **diskon** dibanding nilai wajar.")
elif label == "FAIR":
    st.write("- Valuasi relatif **fair** terhadap nilai wajar.")
elif label == "MAHAL":
    st.write("- Valuasi relatif **mahal**, risiko margin of safety kecil.")

# Bandarmologi context
st.write(f"- Bandarmologi proxy: **{rad['label']}** (OBV / ADL + volume).")

