import re
from typing import List, Tuple
from aliases import CURRENCY_ALIASES
from word_numbers import WORD_NUMBERS

class CurrencyParser:
    def __init__(self):
        self.multipliers = {
            'k': 1000, 'к': 1000, 'thousand': 1000, 'тыс': 1000, 'тысяч': 1000,
            'm': 1000000, 'м': 1000000, 'mil': 1000000, 'млн': 1000000,
            'million': 1000000, 'миллион': 1000000, 'лям': 1000000, 'лимон': 1000000,
            'ляма': 1000000, 'лимона': 1000000, 'миллиона': 1000000, 'миллионов': 1000000
        }

    def parse(self, text: str) -> List[Tuple[float, str]]:
        """Main entry point for currency parsing"""
        # Try each parsing strategy in order of priority
        results = self._try_parse_number_multiplier_currency(text)
        if results:
            return results

        results = self._try_parse_word_number_multiplier_currency(text)
        if results:
            return results

        results = self._try_parse_multiplier_currency(text)
        if results:
            return results

        results = self._try_parse_word_number_currency(text)
        if results:
            return results

        results = self._try_parse_number_currency(text)
        return results

    def _try_parse_number_multiplier_currency(self, text: str) -> List[Tuple[float, str]]:
        """Try to parse text as number + multiplier + currency (e.g., '100k usd', '1.5m eur')"""
        results = []
        pattern = r"(\d+(?:\.\d+)?)\s*((?:k|к|thousand|тыс|тысяч|mil|млн|million|миллион|лям|ляма|лимон|лимона|m|м)(?:illion|llion|л(?:ио)?н(?:ов)?)?)[.\s]*([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

        for match in re.finditer(pattern, text, re.IGNORECASE):
            amount = float(match.group(1))
            multiplier_text = match.group(2)
            currency = match.group(3).lower()

            base_multiplier = multiplier_text.lower().split('illion')[0].split('llion')[0].split('лион')[0].split('лн')[0].rstrip('а').rstrip('ов')
            if base_multiplier in self.multipliers:
                amount *= self.multipliers[base_multiplier]

            self._add_if_valid_currency(results, amount, currency)

        return results

    def _try_parse_word_number_multiplier_currency(self, text: str) -> List[Tuple[float, str]]:
        """Try to parse text as word number + multiplier + currency (e.g., 'два ляма рублей', 'три миллиона долларов')"""
        results = []
        sorted_numbers = sorted(WORD_NUMBERS.keys(), key=len, reverse=True)
        sorted_multipliers = sorted(self.multipliers.keys(), key=len, reverse=True)

        # Pattern matches: word number + multiplier + currency
        pattern = r"(?i)(" + "|".join(map(re.escape, sorted_numbers)) + r")\s+(" + \
                 "|".join(map(re.escape, sorted_multipliers)) + r")\s+([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                number_word = match.group(1).lower()
                multiplier_word = match.group(2).lower()
                currency = match.group(3).lower()

                # Calculate total amount
                base_amount = WORD_NUMBERS[number_word]
                amount = base_amount * self.multipliers[multiplier_word]

                self._add_if_valid_currency(results, amount, currency)
            except (KeyError, ValueError):
                continue

        return results

    def _try_parse_multiplier_currency(self, text: str) -> List[Tuple[float, str]]:
        """Try to parse text as multiplier word + currency (e.g., 'миллион рублей', 'тысяча долларов')"""
        results = []
        sorted_multipliers = sorted(self.multipliers.keys(), key=len, reverse=True)
        pattern = r"(?i)(" + "|".join(map(re.escape, sorted_multipliers)) + r")\s+([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

        for match in re.finditer(pattern, text, re.IGNORECASE):
            multiplier_word = match.group(1).lower()
            currency = match.group(2).lower()
            amount = self.multipliers[multiplier_word]
            self._add_if_valid_currency(results, amount, currency)

        return results

    def _try_parse_word_number_currency(self, text: str) -> List[Tuple[float, str]]:
        """Try to parse text as word number + currency (e.g., 'two hundred dollars', 'двести рублей')"""
        results = []
        sorted_numbers = sorted(WORD_NUMBERS.keys(), key=len, reverse=True)
        pattern = r"(?i)(" + "|".join(map(re.escape, sorted_numbers)) + r")\s+([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                number_word = match.group(1).lower()
                amount = WORD_NUMBERS[number_word]
                currency = match.group(2).lower()
                self._add_if_valid_currency(results, amount, currency)
            except (KeyError, ValueError):
                continue

        return results

    def _try_parse_number_currency(self, text: str) -> List[Tuple[float, str]]:
        """Try to parse text as number + currency (e.g., '100 usd', '50 eur')"""
        results = []
        pattern = r"(\d+(?:\.\d+)?)[.\s]*([a-zA-Zа-яА-Я€$¥£₽₴кчКЧ]+)"

        for match in re.finditer(pattern, text, re.IGNORECASE):
            amount = float(match.group(1))
            currency = match.group(2).lower()
            self._add_if_valid_currency(results, amount, currency)

        return results

    def _add_if_valid_currency(self, results: List[Tuple[float, str]], amount: float, currency: str):
        """Helper method to add amount and currency if the currency is valid"""
        for alias, code in CURRENCY_ALIASES.items():
            if currency.startswith(alias) or currency == alias:
                results.append((amount, code))
                break
