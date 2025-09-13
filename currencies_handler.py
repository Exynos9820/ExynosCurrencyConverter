import requests
import json
from datetime import datetime, timedelta

class CurrenciesHandler:
    def __init__(self, api_url, currencies, token=None, cache_file="rates_cache.json", cache_ttl=3600):
        """
        :param api_url: Base API URL for CurrencyAPI (e.g. https://api.currencyapi.com/v3/latest)
        :param currencies: List of supported currencies (e.g. ["EUR", "GBP", "JPY", "CZK"])
        :param token: API key for CurrencyAPI
        :param cache_file: File path to cache exchange rates
        :param cache_ttl: Time to live for cache in seconds
        """
        self.api_url = api_url
        self.currencies = currencies
        self.token = token
        self.cache_file = cache_file
        self.cache_ttl = timedelta(seconds=cache_ttl)
        self.last_fetched_time = None
        self.cached_rates = {}
        self.read_cache()

    def read_cache(self):
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                self.last_fetched_time = datetime.fromisoformat(data["timestamp"])
                self.cached_rates = data["rates"]
        except (FileNotFoundError, KeyError, ValueError):
            self.last_fetched_time = None
            self.cached_rates = {}

    def save_cache(self, rates: dict):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "rates": rates
        }
        with open(self.cache_file, "w") as f:
            json.dump(data, f)
        self.last_fetched_time = datetime.utcnow()
        self.cached_rates = rates

    def fetch_exchange_rates(self, base: str) -> dict:
        """Fetches fresh rates from CurrencyAPI or returns cache if valid"""
        if (
            self.last_fetched_time
            and datetime.utcnow() - self.last_fetched_time < self.cache_ttl
            and base in self.cached_rates
        ):
            return self.cached_rates[base]

        # Fetch from CurrencyAPI
        response = requests.get(
            self.api_url,
            params={
                "apikey": self.token,
                "base_currency": base,
                "currencies": ",".join([c for c in self.currencies if c != base])
            },
        )
        response.raise_for_status()
        data = response.json()
        print("Fetched new rates:", data)

        # Parse response: {"data": {"EUR": {"value": 0.92}, "GBP": {"value": 0.79}, ...}}
        rates = {code: info["value"] for code, info in data["data"].items()}

        # Update cache (per base currency)
        if not self.cached_rates:
            self.cached_rates = {}
        self.cached_rates[base] = rates
        self.save_cache(self.cached_rates)

        return rates

    def get_converted_amount(self, amount, rate):
        return amount * rate

    def get_converted_amounts(self, amount, base):
        rates = self.fetch_exchange_rates(base)  # This now returns the rates for the specific base currency
        converted = {}
        for cur in self.currencies:
            if cur == base:
                continue
            if cur in rates:
                converted[cur] = self.get_converted_amount(amount, rates[cur])
        return converted
