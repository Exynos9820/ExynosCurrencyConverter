from ast import Dict
import html
from aliases import CURRENCY_EMOJIS


class ReplyBuilder:
    def _emoji_for(self, iso: str) -> str:
        return CURRENCY_EMOJIS.get(iso.upper(), iso.upper())

    def build_html(self, amount: float, base: str, rates: dict) -> str:
        safe_amount = html.escape(f"{amount:g}")
        header = f"<b>{safe_amount} {html.escape(base)}</b>:\n"

        lines = []
        for currency, rate in sorted(rates.items()):
            if currency.upper() == base.upper():
                continue
            try:
                converted = float(rate)
            except Exception:
                continue
            emoji = html.escape(self._emoji_for(currency))
            lines.append(f"{emoji} <b>{converted:,.2f}</b> <code>{html.escape(currency)}</code>")

        body = "\n".join(lines) if lines else "<i>No supported target currencies returned.</i>"
        return header + body
