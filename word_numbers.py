# Word to number mapping
WORD_NUMBERS = {
    # Basic numbers
    'zero': 0, 'один': 1, 'одна': 1, 'one': 1, 'два': 2, 'две': 2, 'two': 2,
    'три': 3, 'three': 3, 'четыре': 4, 'four': 4, 'пять': 5, 'five': 5,
    'шесть': 6, 'six': 6, 'семь': 7, 'seven': 7, 'восемь': 8, 'eight': 8,
    'девять': 9, 'nine': 9, 'десять': 10, 'ten': 10,

    # Teens
    'одиннадцать': 11, 'eleven': 11, 'двенадцать': 12, 'twelve': 12,
    'тринадцать': 13, 'thirteen': 13, 'четырнадцать': 14, 'fourteen': 14,
    'пятнадцать': 15, 'fifteen': 15, 'шестнадцать': 16, 'sixteen': 16,
    'семнадцать': 17, 'seventeen': 17, 'восемнадцать': 18, 'eighteen': 18,
    'девятнадцать': 19, 'nineteen': 19,

    # Tens
    'двадцать': 20, 'twenty': 20, 'тридцать': 30, 'thirty': 30,
    'сорок': 40, 'forty': 40, 'пятьдесят': 50, 'fifty': 50,
    'шестьдесят': 60, 'sixty': 60, 'семьдесят': 70, 'seventy': 70,
    'восемьдесят': 80, 'eighty': 80, 'девяносто': 90, 'ninety': 90,

    # Hundreds
    'сто': 100, 'hundred': 100, 'двести': 200, 'триста': 300,
    'четыреста': 400, 'пятьсот': 500, 'шестьсот': 600,
    'семьсот': 700, 'восемьсот': 800, 'девятьсот': 900,

    # Thousands
    'тысяча': 1000, 'thousand': 1000, 'тысячи': 1000, 'тысяч': 1000
}

def word_to_number(word_str: str) -> float:
    """Convert word numbers to actual numbers"""
    words = word_str.lower().split()
    total = 0
    current = 0

    for word in words:
        if word in ['and', 'и']:
            continue

        if word in WORD_NUMBERS:
            num = WORD_NUMBERS[word]
            if num == 100:  # handle hundreds
                if current == 0:
                    current = 1
                current *= num
            elif num == 1000:  # handle thousands
                if current == 0:
                    current = 1
                current *= num
                total += current
                current = 0
            else:
                if current == 0:
                    current = num
                else:
                    current += num

    return float(total + current)
