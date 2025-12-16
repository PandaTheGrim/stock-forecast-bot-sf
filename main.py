from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

from config.constants import TOKEN, TICKER, AMOUNT
from services.bot import StockForecastingBot


def main():
    bot = StockForecastingBot()

    application = Application.builder().token(TOKEN).build()
    application.add_handlers([
        CommandHandler("start", bot.start),
        ConversationHandler(
            entry_points=[CommandHandler('forecast', bot.forecast)],
            states={
                TICKER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.ticker)],
                AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_amount)],
            },
            fallbacks=[CommandHandler('cancel', bot.cancel)],
        )
    ])

    print("Bot starting...")
    application.run_polling()
    print("Bot started!")


if __name__ == '__main__':
    main()