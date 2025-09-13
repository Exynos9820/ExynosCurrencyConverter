from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import re
import os
from dotenv import load_dotenv
from currencies_handler import CurrenciesHandler
from reply_builder import ReplyBuilder
from aliases import CURRENCY_ALIASES, CURRENCIES

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
load_dotenv()

API_URL = os.getenv("API_URL")
TOKEN_API = os.getenv("TOKEN_API")
handler = CurrenciesHandler(API_URL, CURRENCIES, TOKEN_API)
reply_builder = ReplyBuilder()

def try_parse_number_multiplier_currency(text: str) -> list:
    """Try to parse text as number + multiplier + currency (e.g., '100k usd', '1.5m eur')"""
    results = []
    pattern = r"(\d+(?:\.\d+)?)\s*((?:k|к|thousand|тыс|тысяч|mil|млн|million|миллион|лям|ляма|лимон|лимона|m|м)(?:illion|llion|л(?:ио)?н(?:ов)?)?)[.\s]*([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

    multipliers = {
        'k': 1000, 'к': 1000, 'thousand': 1000, 'тыс': 1000, 'тысяч': 1000,
        'm': 1000000, 'м': 1000000, 'mil': 1000000, 'млн': 1000000,
        'million': 1000000, 'миллион': 1000000, 'лям': 1000000, 'лимон': 1000000,
        'ляма': 1000000, 'лимона': 1000000
    }

    for match in re.finditer(pattern, text, re.IGNORECASE):
        amount = float(match.group(1))
        multiplier_text = match.group(2)
        currency = match.group(3).lower()

        # Extract base multiplier
        base_multiplier = multiplier_text.lower().split('illion')[0].split('llion')[0].split('лион')[0].split('лн')[0].rstrip('а').rstrip('ов')
        if base_multiplier in multipliers:
            amount *= multipliers[base_multiplier]

        for alias, code in CURRENCY_ALIASES.items():
            if currency.startswith(alias) or currency == alias:
                results.append((amount, code))
                break

    return results

def try_parse_word_number_currency(text: str) -> list:
    """Try to parse text as word number + currency (e.g., 'two hundred dollars', 'двести рублей')"""
    results = []
    sorted_numbers = sorted(WORD_NUMBERS.keys(), key=len, reverse=True)
    pattern = r"(?i)(" + "|".join(map(re.escape, sorted_numbers)) + r")\s+([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

    for match in re.finditer(pattern, text, re.IGNORECASE):
        try:
            number_word = match.group(1).lower()
            amount = WORD_NUMBERS[number_word]
            currency = match.group(2).lower()

            for alias, code in CURRENCY_ALIASES.items():
                if currency.startswith(alias) or currency == alias:
                    results.append((amount, code))
                    break
        except (KeyError, ValueError):
            continue

    return results

def try_parse_number_currency(text: str) -> list:
    """Try to parse text as number + currency (e.g., '100 usd', '50 eur')"""
    results = []
    pattern = r"(\d+(?:\.\d+)?)[.\s]*([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

    for match in re.finditer(pattern, text, re.IGNORECASE):
        amount = float(match.group(1))
        currency = match.group(2).lower()

        for alias, code in CURRENCY_ALIASES.items():
            if currency.startswith(alias) or currency == alias:
                results.append((amount, code))
                break

    return results

def try_parse_multiplier_currency(text: str) -> list:
    """Try to parse text as multiplier word + currency (e.g., 'миллион рублей', 'тысяча долларов')"""
    results = []
    multipliers = {
        'thousand': 1000, 'тысяча': 1000, 'тысячи': 1000, 'тысяч': 1000,
        'million': 1000000, 'миллион': 1000000, 'миллиона': 1000000, 'миллионов': 1000000,
        'лям': 1000000, 'лимон': 1000000, 'ляма': 1000000, 'лимона': 1000000
    }

    # Create pattern with all multiplier words, sorted by length for better matching
    sorted_multipliers = sorted(multipliers.keys(), key=len, reverse=True)
    pattern = r"(?i)(" + "|".join(map(re.escape, sorted_multipliers)) + r")\s+([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

    for match in re.finditer(pattern, text, re.IGNORECASE):
        multiplier_word = match.group(1).lower()
        currency = match.group(2).lower()

        amount = multipliers[multiplier_word]

        for alias, code in CURRENCY_ALIASES.items():
            if currency.startswith(alias) or currency == alias:
                results.append((amount, code))
                break

    return results

def detect_currencies(text: str):
    """Find all amount + currency pairs in text using different parsing strategies"""
    # Try each parsing strategy in order of priority
    results = try_parse_number_multiplier_currency(text)
    if results:
        return results

    results = try_parse_multiplier_currency(text)
    if results:
        return results

    results = try_parse_word_number_currency(text)
    if results:
        return results

    results = try_parse_number_currency(text)
    return results

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    currency_pairs = detect_currencies(text)
    if not currency_pairs:
        print("No amount or base currency detected")
        return

    all_replies = []
    for amount, base in currency_pairs:
        rates = handler.fetch_exchange_rates(base)
        if not rates:
            continue
        result = handler.get_converted_amounts(amount, base)
        reply = reply_builder.build_html(amount, base, result)
        all_replies.append(reply)

    if not all_replies:
        await update.message.reply_text("Could not fetch exchange rates.")
        return

    # Join all replies with double newlines for better readability
    final_reply = "\n\n".join(all_replies)

    # Create inline keyboard with delete button
    keyboard = [[InlineKeyboardButton("🗑 Delete", callback_data="delete")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        final_reply,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()  # Answer the callback query to stop the loading state

    if query.data == "delete":
        await query.message.delete()

def main():
    TOKEN_BOT = os.getenv("TOKEN_BOT")
    app = Application.builder().token(TOKEN_BOT).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))  # Add handler for button callbacks
    app.run_polling()

if __name__ == "__main__":
    main()
