def score_all(fund_ok: bool, valuation_label: str, tech_ok: bool, radar_label: str):
    # 0-100
    score = 0

    # Fundamental (35)
    score += 35 if fund_ok else 10

    # Valuation (25)
    if valuation_label == "DISKON":
        score += 25
    elif valuation_label == "FAIR":
        score += 15
    elif valuation_label == "MAHAL":
        score += 5
    else:
        score += 10

    # Technical (25)
    score += 25 if tech_ok else 10

    # Bandarmologi (15)
    if radar_label == "AKUMULASI":
        score += 15
    elif radar_label == "NETRAL":
        score += 8
    else:
        score += 3

    return min(100, score)

def verdict(score: int, tech_ok: bool, valuation_label: str):
    # Gate: kalau teknikal invalid, jangan BUY walaupun diskon
    if score >= 75 and tech_ok and valuation_label != "MAHAL":
        return "BUY"
    if score <= 45 and valuation_label == "MAHAL":
        return "SELL"
    return "HOLD"
