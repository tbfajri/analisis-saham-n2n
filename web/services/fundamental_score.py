# services/fundamental_score.py
import math

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def score_growth(rev_yoy, ni_yoy):
    s = 0
    reasons = []

    if rev_yoy is not None:
        if rev_yoy >= 10: s += 15; reasons.append("Revenue tumbuh kuat")
        elif rev_yoy >= 5: s += 10; reasons.append("Revenue tumbuh moderat")
        elif rev_yoy > 0: s += 5; reasons.append("Revenue tumbuh tipis")
        else: reasons.append("Revenue stagnan/menurun")

    if ni_yoy is not None:
        if ni_yoy >= 10: s += 15; reasons.append("Laba tumbuh kuat")
        elif ni_yoy >= 5: s += 10; reasons.append("Laba tumbuh moderat")
        elif ni_yoy > 0: s += 5; reasons.append("Laba tumbuh tipis")
        else: reasons.append("Laba stagnan/menurun")

    return clamp(s, 0, 30), reasons

def score_profitability(gm, nm, roe):
    s = 0
    reasons = []

    if gm is not None:
        if gm >= 0.4: s += 10; reasons.append("Gross margin sangat sehat")
        elif gm >= 0.25: s += 7; reasons.append("Gross margin sehat")
        elif gm >= 0.15: s += 4; reasons.append("Gross margin tipis")

    if nm is not None:
        if nm >= 0.2: s += 10; reasons.append("Net margin tinggi")
        elif nm >= 0.1: s += 7; reasons.append("Net margin sehat")
        elif nm >= 0.05: s += 4; reasons.append("Net margin tipis")

    if roe is not None:
        if roe >= 20: s += 10; reasons.append("ROE sangat kuat")
        elif roe >= 15: s += 7; reasons.append("ROE sehat")
        elif roe >= 10: s += 4; reasons.append("ROE cukup")

    return clamp(s, 0, 30), reasons

def score_health(de_ratio, equity_ratio):
    s = 0
    reasons = []

    if de_ratio is not None:
        if de_ratio <= 0.5: s += 12; reasons.append("Utang rendah")
        elif de_ratio <= 1.0: s += 8; reasons.append("Utang terkontrol")
        elif de_ratio <= 2.0: s += 4; reasons.append("Utang cukup tinggi")
        else: reasons.append("Utang tinggi")

    if equity_ratio is not None:
        if equity_ratio >= 0.5: s += 13; reasons.append("Equity kuat")
        elif equity_ratio >= 0.3: s += 8; reasons.append("Equity cukup")
        else: reasons.append("Equity lemah")

    return clamp(s, 0, 25), reasons

def score_cashflow(fcf_series):
    s = 0
    reasons = []

    if fcf_series is None or len(fcf_series) == 0:
        return 0, ["Data FCF tidak tersedia"]

    positives = (fcf_series > 0).sum()
    total = len(fcf_series)

    if positives == total:
        s = 15; reasons.append("FCF konsisten positif")
    elif positives >= total - 1:
        s = 10; reasons.append("FCF mayoritas positif")
    elif positives >= total / 2:
        s = 5; reasons.append("FCF fluktuatif")
    else:
        reasons.append("FCF sering negatif")

    return clamp(s, 0, 15), reasons

def grade_from_score(score):
    if score >= 85: return "A"
    if score >= 75: return "A-"
    if score >= 65: return "B+"
    if score >= 55: return "B"
    if score >= 45: return "C"
    return "D"

def fundamental_score(inputs):
    total = 0
    reasons = []

    s, r = score_growth(inputs.get("rev_yoy"), inputs.get("ni_yoy"))
    total += s; reasons += r

    s, r = score_profitability(inputs.get("gross_margin"), inputs.get("net_margin"), inputs.get("roe"))
    total += s; reasons += r

    s, r = score_health(inputs.get("de_ratio"), inputs.get("equity_ratio"))
    total += s; reasons += r

    s, r = score_cashflow(inputs.get("fcf_series"))
    total += s; reasons += r

    total = clamp(total, 0, 100)
    grade = grade_from_score(total)

    return {
        "score": total,
        "grade": grade,
        "reasons": reasons
    }
