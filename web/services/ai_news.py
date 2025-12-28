import os
import google.generativeai as genai

def gemini_news_summary(news_items, max_words=120):
    """
    news_items = list of dict:
    [
      {"title": "...", "source": "...", "published": "..."},
      ...
    ]
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key tidak ditemukan."

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-flash")

    # ---- build structured input
    bullets = []
    for n in news_items[:8]:  # batasi biar hemat token
        bullets.append(
            f"- {n.get('title')} ({n.get('source','')}, {n.get('published','')})"
        )

    news_text = "\n".join(bullets)

    prompt = f"""
    Kamu adalah asisten analis saham profesional.

    Tugas kamu adalah MERANGKUM berita berikut untuk investor saham Indonesia.

    Instruksi:
    1. Gunakan BAHASA INDONESIA yang jelas dan netral
    2. Klasifikasikan jenis berita:
    - Operasional
    - Keuangan
    - Struktural / Strategis
    3. Nilai dampak berita terhadap fundamental perusahaan:
    LOW / MEDIUM / HIGH
    4. Soroti potensi risiko tersembunyi jika ada
    5. Buat ringkasan singkat dan padat (maksimal {max_words} kata)

    Larangan:
    - Jangan memprediksi harga saham
    - Jangan memberi rekomendasi BUY / SELL
    - Jangan menggunakan bahasa promosi atau sensasional

    Berita:
    {news_text}

    Format output:
    Ringkasan singkat dalam paragraf,
    diakhiri dengan kesimpulan dampak berita.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gagal generate AI summary: {e}"
