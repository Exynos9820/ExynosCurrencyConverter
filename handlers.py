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

        lines = [line for line in final_reply.split("\n") if line.strip()]
        header_reply = [l for l in lines if "USD" in l][0]

        # Create inline keyboard with show and delete buttons
        keyboard = [
            [
                InlineKeyboardButton("Show", callback_data="show"),
                InlineKeyboardButton("🗑 Delete", callback_data="delete")
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = await update.message.reply_text(
            header_reply,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )

        # store the state and both text versions in the user_data cache
        context.bot_data.setdefault("currency_cache", {})
            
        cache_key = (update.effective_chat.id, msg.message_id)
        context.bot_data["currency_cache"][cache_key] = {
            "full": final_reply,
            "min": header_reply,
            # track whether the message is currently open or closed
            "expanded": False
        }

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        # get the cached strings for this specific message
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        cache_key = (chat_id, message_id)
        cache = context.bot_data.get("currency_cache", {}).get(cache_key)
        
        if query.data == "delete":
            await query.answer()
            # clean up the cache to prevent memory leak
            # we are not telegram devs and can't afford that
            if "currency_cache" in context.user_data:
                context.user_data["currency_cache"].pop(cache_key, None)
            await query.message.delete()
            return # stop the execution

        elif query.data == "show":
            await query.answer()  # removes the loading spinner animation on the button
            
            # fallback if the bot process restarted and wiped the volatile RAM cache
            if not cache:
                await query.message.edit_text(
                    "Data expired or bot was restarted",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 Delete", callback_data="delete")]])
                )
                return

            # invert the current boolean toggle state
            cache["expanded"] = not cache["expanded"]
            
            # choose text format and button indicator text based on the active state
            if cache["expanded"]:
                text_to_show = cache["full"]
                button_label = "Hide"
            else:
                text_to_show = cache["min"]
                button_label = "Show"

            # rebuild the interface with the new dynamic toggle label
            keyboard = [
                [
                    InlineKeyboardButton(button_label, callback_data="show"),
                    InlineKeyboardButton("🗑 Delete", callback_data="delete")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # apply modifications
            await query.message.edit_text(
                text_to_show,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        else:
            await query.answer()
