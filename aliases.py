CURRENCY_ALIAS_GROUPS = {
    "USD": ["usd", "dollar", "dollars", "$", "bucks", "us$", "us dollar", "usdollar", "американский доллар", "доллар", "доллары", "доллара", "долларов", "бакс", "баксы", "баксов"],
    "EUR": ["eur", "euro", "euros", "€", "eur$", "european currency", "евро", "еврики", "еврик", "евриков"],
    "GBP": ["gbp", "pound", "pounds", "£", "quid", "sterling", "british pound", "британский фунт", "фунт", "фунты", "фунта", "фунтов"],
    "JPY": ["jpy", "yen", "¥", "japan yen", "japanese yen", "иена", "японская иена", "японские иены", "иен"],
    "CZK": ["czk", "koruna", "korunas", "kč", "czech crown", "czech koruna", "крона", "чешская крона", "крон", "кроны"],
    "UAH": ["uah", "грн", "hryvnia", "hryvnias", "ukrainian hryvnia", "украинская гривна", "гривна", "гривны", "гривен"],
    "RUB": ["rub", "₽", "ruble", "rubles", "russian ruble", "russian rubles", "российский рубль", "рубль", "руб", "рубли", "рублей", "рубля", "срубли", "срублей", "срубля"],
    "KZT": ["kzt", "₸", "tenge", "тенге", "казахстанский тенге", "казахстанские тенге", "казахстанских тенге"],
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
    "KZT": "🇰🇿 ₸",
}
