def currency_brl(value: float) -> str:
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def integer_br(value: int | float) -> str:
    return f"{int(value):,}".replace(",", ".")


def percentage_br(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def delta_percentage(value: float | None) -> str | None:
    return None if value is None else percentage_br(value)
