# 📈 StockLab — End-to-End Analisis Saham IDX

StockLab adalah aplikasi **analisis saham Indonesia (IDX)** berbasis **Streamlit** yang menggabungkan:
- Fundamental analysis
- Valuation (fair value)
- Technical analysis
- Bandarmologi (orderflow proxy)
- Scoring & final verdict (BUY / HOLD / SELL)

Project ini dibuat untuk membantu **pengambilan keputusan investasi yang objektif dan terstruktur**.

---

## 🚀 Fitur Utama

### 1️⃣ Profil Perusahaan
- Nama, sektor, industri
- Market cap
- Deskripsi bisnis

### 2️⃣ Berita Terkait Saham
- Headline berita terbaru
- Klik langsung ke sumber (tab baru)

### 3️⃣ Statistik Keuangan (5 Tahun)
- Income Statement
- Balance Sheet
- Cashflow
- Format angka Rupiah

### 4️⃣ Valuation (Nilai Wajar)
- Fair Value berbasis **PE**
- Fair Value berbasis **PBV**
- Fair Value Combined
- Diskon / Premium (%) vs harga terbaru
- Klasifikasi: **DISKON / FAIR / MAHAL**

### 5️⃣ Technical Analysis
- Candlestick + EMA 20 / 50 / 200
- RSI & volume
- Rekomendasi:
  - Entry range
  - Stoploss
  - Take profit (Risk : Reward)

### 6️⃣ Bandarmologi (Proxy)
- Analisis volume & price behavior
- Indikasi: Akumulasi / Distribusi / Netral

### 7️⃣ Fundamental Scoring
- Growth
- Profitability
- Financial health
- Cashflow quality
- Skor 0–100 + Grade (A–D)

### 8️⃣ Final Verdict Engine
Menggabungkan:
- Fundamental score
- Valuation
- Technical setup
- Bandarmologi

➡️ Output akhir:
**BUY / HOLD / SELL + Confidence Level**

---

## 🧠 Filosofi Analisis

> **Fundamental = kualitas bisnis**  
> **Valuation = harga yang dibayar**  
> **Technical = timing masuk**  

Tidak ada BUY jika fundamental lemah, walaupun chart terlihat bagus.

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **Streamlit**
- **Pandas / NumPy**
- **Plotly**
- **yfinance**
- **RSS News (Google News)**

---

## 📂 Struktur Project

```
.
├── app.py
├── watchlist.txt
├── services/
│ ├── data.py
│ ├── news.py
│ ├── technical.py
│ ├── financials.py
│ ├── valuation.py
│ ├── orderflow.py
│ ├── fundamental_score.py
│ └── verdict_engine.py
├── utils.py
├── requirements.txt
└── README.md
```

---

## ▶️ Menjalankan di Local

### 1️⃣ Install dependency
```bash
pip install -r requirements.txt
```

### 2️⃣ Jalankan aplikasi
```bash
streamlit run app.py --server.address localhost --server.port 8501
```
