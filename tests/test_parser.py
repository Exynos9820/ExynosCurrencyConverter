import pytest
from currency_parser import CurrencyParser


@pytest.fixture
def parser():
    """Fixture to create a CurrencyParser instance for each test"""
    return CurrencyParser()


class TestNumberCurrency:
    """Test basic number + currency patterns"""

    def test_simple_number_with_currency(self, parser):
        result = parser.parse("100 usd")
        assert result == [(100.0, 'USD')]
        result = parser.parse("250 рублей")
        assert result == [(250.0, 'RUB')]
        result = parser.parse("75.25 фунтов")
        assert result == [(75.25, 'GBP')]
        result = parser.parse("1000 крон")
        assert result == [(1000.0, 'CZK')]

    def test_decimal_number_with_currency(self, parser):
        result = parser.parse("50.5 eur")
        assert result == [(50.5, 'EUR')]


class TestNumberMultiplierCurrency:
    """Test number + multiplier + currency patterns"""

    def test_number_with_k_multiplier(self, parser):
        result = parser.parse("100k usd")
        assert result == [(100000.0, 'USD')]
        result = parser.parse("100к гривен")
        assert result == [(100000.0, 'UAH')]
        result = parser.parse("100k рублей")
        assert result == [(100000.0, 'RUB')]
        result = parser.parse("15k крон")
        assert result == [(15000.0, 'CZK')]

    def test_number_with_million_multiplier(self, parser):
        result = parser.parse("1.5m eur")
        assert result == [(1500000.0, 'EUR')]


class TestWordNumberCurrency:
    """Test word number + currency patterns"""

    def test_word_number_russian(self, parser):
        result = parser.parse("сто рублей")
        assert result == [(100.0, 'RUB')]

    def test_word_number_english(self, parser):
        result = parser.parse("fifty dollars")
        assert result == [(50.0, 'USD')]


class TestWordNumberMultiplierCurrency:
    """Test word number + multiplier + currency patterns"""

    def test_word_number_with_multiplier_russian(self, parser):
        result = parser.parse("два ляма рублей")
        assert result == [(2000000.0, 'RUB')]

    def test_unexpected_quires(self, parser):
        # Test that non-currency words do not produce results
        result = parser.parse("кубик рубика")
        assert result == []
        result = parser.parse("кк рубля")
        assert result == []


class TestMultipleCurrencies:
    """Test parsing multiple currencies from one text"""

    def test_multiple_currencies_in_text(self, parser):
        result = parser.parse("I have 100 usd and 50 eur")
        assert len(result) == 2
        assert (100.0, 'USD') in result
        assert (50.0, 'EUR') in result


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_no_currency_found(self, parser):
        result = parser.parse("just some text without currency")
        assert result == []

    def test_empty_string(self, parser):
        result = parser.parse("")
        assert result == []

    def test_false_positive_k_preposition(self, parser):
        # "к европейскому" should not be parsed (к is a preposition, европейскому is not a currency)
        result = parser.parse("к европейскому")
        assert result == []

    def test_tysiachi_kron(self, parser):
        # "92 тысячи крон" should be parsed as 92000 CZK
        result = parser.parse("92 тысячи крон")
        assert result == [(92000.0, 'CZK')]
