CURRENCY_ALIAS_GROUPS = {
    "USD": ["usd", "dollar", "dollars", "$", "bucks", "us$", "us dollar", "usdollar"],
    "EUR": ["eur", "euro", "euros", "€", "eur$", "european currency"],
    "GBP": ["gbp", "pound", "pounds", "£", "quid", "sterling"],
    "JPY": ["jpy", "yen", "¥", "japan yen", "japanese yen"],
    "CZK": ["czk", "koruna", "korunas", "kč", "czech crown", "czech koruna", "крона", "чешская крона", "крон"],
    "UAH": ["uah", "грн", "hryvnia", "hryvnias", "ukrainian hryvnia", "украинская гривна", "гривна", "гривны", "гривен"],
    "RUB": ["rub", "₽", "ruble", "rubles", "russian ruble", "russian rubles", "российский рубль", "рубль", "руб", "рубли", "рублей"],
}

CURRENCY_ALIASES = {
    alias.lower(): code
    for code, aliases in CURRENCY_ALIAS_GROUPS.items()
    for alias in aliases
}

CURRENCIES = list(CURRENCY_ALIAS_GROUPS.keys())

CURRENCY_EMOJIS = {
    "USD": "🇺🇸 $",
    "EUR": "🇪🇺 €",
    "GBP": "🇬🇧 £",
    "JPY": "🇯🇵 ¥",
    "CZK": "🇨🇿 Kč",
    "UAH": "🇺🇦 ₴",
    "RUB": "🏳️‍⚧️ ₽",
}
