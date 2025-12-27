def classify_valuation(last_price: float, fair_value: float, band=0.10):
    if fair_value <= 0:
        return "UNKNOWN"
    diff = (fair_value - last_price) / fair_value
    if diff >= band:
        return "DISKON"
    if diff <= -band:
        return "MAHAL"
    return "FAIR"

def fair_value_pe(last_eps: float, target_pe: float) -> float:
    if last_eps is None or last_eps <= 0 or target_pe <= 0:
        return 0.0
    return last_eps * target_pe

def fair_value_pbv(book_value_per_share: float, target_pbv: float) -> float:
    if book_value_per_share is None or book_value_per_share <= 0 or target_pbv <= 0:
        return 0.0
    return book_value_per_share * target_pbv
