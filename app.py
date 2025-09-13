import os
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
from currencies_handler import CurrenciesHandler
from reply_builder import ReplyBuilder
from handlers import CurrencyMessageHandler
from aliases import CURRENCIES

def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    api_url = os.getenv("API_URL")
    token_api = os.getenv("TOKEN_API")
    token_bot = os.getenv("TOKEN_BOT")

    # Create service instances
    currencies_handler = CurrenciesHandler(api_url, CURRENCIES, token_api)
    reply_builder = ReplyBuilder()
    currency_handler = CurrencyMessageHandler(currencies_handler, reply_builder)

    # Set up the application
    app = Application.builder().token(token_bot).build()

    # Add handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, currency_handler.handle_message))
    app.add_handler(CallbackQueryHandler(currency_handler.handle_callback))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()

def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    api_url = os.getenv("API_URL")
    token_api = os.getenv("TOKEN_API")
    token_bot = os.getenv("TOKEN_BOT")

    # Create service instances
    currencies_handler = CurrenciesHandler(api_url, CURRENCIES, token_api)
    reply_builder = ReplyBuilder()
    currency_handler = CurrencyMessageHandler(currencies_handler, reply_builder)

    # Set up the application
    app = Application.builder().token(token_bot).build()

    # Add handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, currency_handler.handle_message))
    app.add_handler(CallbackQueryHandler(currency_handler.handle_callback))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
