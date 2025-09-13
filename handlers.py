from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from currencies_handler import CurrenciesHandler
from reply_builder import ReplyBuilder
from currency_parser import CurrencyParser
from rate_limiter import RateLimiter

class CurrencyMessageHandler:
    def __init__(self, currencies_handler: CurrenciesHandler, reply_builder: ReplyBuilder,
                 allowed_user_ids: str, allowed_chat_ids: str):
        self.currency_parser = CurrencyParser()
        self.currencies_handler = currencies_handler
        self.reply_builder = reply_builder
        self.allowed_user_ids = allowed_user_ids
        self.allowed_chat_ids = allowed_chat_ids
        self.rate_limiter = RateLimiter(limit=5, window=60)  # 5 requests per minute
        self.max_values_per_message = 5  # Maximum number of currency values per message

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages with currency amounts"""
        # if chat is allowed, then we reply even if user is not in allowed users
        if self.allowed_chat_ids:
            chat_id_str = str(update.effective_chat.id)
            if chat_id_str not in self.allowed_chat_ids.split(","):
                print(f"Chat {chat_id_str} not in allowed chats, ignoring.")
                return

        text = update.message.text
        currency_pairs = self.currency_parser.parse(text)
        if not currency_pairs:
            print("No amount or base currency detected")
            return

        # Only check rate limit if we found currency pairs
        user_id = update.effective_user.id
        if not self.rate_limiter.is_allowed(user_id):
            remaining_time = self.rate_limiter.get_remaining_time(user_id)
            await update.message.reply_text(
                f"⏳ Please wait {remaining_time} seconds before making another request.",
                parse_mode="HTML"
            )
            return

        # If there are more than max values, take only the first max_values
        if len(currency_pairs) > self.max_values_per_message:
            currency_pairs = currency_pairs[:self.max_values_per_message]

        all_replies = []
        for amount, base in currency_pairs:
            rates = self.currencies_handler.fetch_exchange_rates(base)
            if not rates:
                continue
            result = self.currencies_handler.get_converted_amounts(amount, base)
            reply = self.reply_builder.build_html(amount, base, result)
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

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()  # Answer the callback query to stop the loading state

        if query.data == "delete":
            await query.message.delete()
