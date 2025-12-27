# services/verdict_engine.py
def final_verdict(
    fundamental_score: int,
    valuation_label: str,
    technical_ok: bool,
    bandarmologi_label: str,
):
    reasons = []

    # --- Fundamental gate
    if fundamental_score < 55:
        return {
            "verdict": "SELL / AVOID",
            "confidence": "LOW",
            "reasons": ["Fundamental lemah (score < 55)"]
        }

    # --- Strong fundamental
    if fundamental_score >= 75:
        if technical_ok and valuation_label in ("DISKON", "FAIR"):
            reasons.append("Fundamental kuat")
            reasons.append(f"Valuasi {valuation_label.lower()}")
            reasons.append("Setup teknikal valid")
            if bandarmologi_label == "AKUMULASI":
                reasons.append("Terindikasi akumulasi")
            return {
                "verdict": "BUY",
                "confidence": "HIGH",
                "reasons": reasons
            }
        else:
            return {
                "verdict": "HOLD",
                "confidence": "MEDIUM",
                "reasons": ["Fundamental kuat, tapi timing belum ideal"]
            }

    # --- Medium fundamental
    if 65 <= fundamental_score < 75:
        if valuation_label == "DISKON" and technical_ok:
            return {
                "verdict": "BUY (Speculative)",
                "confidence": "MEDIUM",
                "reasons": [
                    "Fundamental cukup baik",
                    "Valuasi diskon",
                    "Setup teknikal valid"
                ]
            }
        return {
            "verdict": "HOLD",
            "confidence": "MEDIUM",
            "reasons": ["Fundamental cukup baik, tunggu konfirmasi"]
        }

    # --- Borderline
    return {
        "verdict": "HOLD / REDUCE",
        "confidence": "LOW",
        "reasons": ["Fundamental borderline"]
    }
