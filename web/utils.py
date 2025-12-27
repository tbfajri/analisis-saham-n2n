def rupiah(x, digits=0):
    if x is None:
        return "-"
    try:
        x = float(x)
    except Exception:
        return "-"
    fmt = f"{{:,.{digits}f}}".format(x)
    return "Rp " + fmt.replace(",", ".")


def rupiah_short(x):
    if x is None:
        return "-"
    try:
        x = float(x)
    except Exception:
        return "-"

    abs_x = abs(x)
    if abs_x >= 1_000_000_000_000:
        return f"Rp {x/1_000_000_000_000:,.2f} T".replace(",", ".")
    elif abs_x >= 1_000_000_000:
        return f"Rp {x/1_000_000_000:,.2f} M".replace(",", ".")
    elif abs_x >= 1_000_000:
        return f"Rp {x/1_000_000:,.2f} Jt".replace(",", ".")
    else:
        return f"Rp {x:,.0f}".replace(",", ".")
