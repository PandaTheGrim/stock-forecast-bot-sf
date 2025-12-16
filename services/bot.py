from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from config.constants import TICKER, AMOUNT
from models.calculate_trading_strategy import calculate_trading_strategy
from models.create_forecast_plot import create_forecast_plot
from models.generate_forecast import generate_forecast
from models.train_models import train_models
from services.ticker_history import get_ticker_history
from utils.logger import log_request, log_error
from utils.response import format_response


class StockForecastingBot:
    """
    Основной класс telegram-бота, реализующий взаимодействие с пользователем
    """

    def __init__(self):
        # путь к лог‑файлу
        self.log_file = "logs.txt"

    @staticmethod
    async def start(update: Update, _: CallbackContext) -> None:
        """
        Обрабатывает команду /start: отправляет сообщение‑приглашение для начала работы с ботом
        """
        await update.message.reply_text('To get started, enter the /forecast command.')

    @staticmethod
    async def forecast(update: Update, _: CallbackContext) -> int:
        """
        Шаг 1. Запрос тикера
        """
        await update.message.reply_text('Enter the company ticker (for example, AAPL, MSFT, GOOGL).')

        return TICKER

    @staticmethod
    async def ticker(update: Update, context: CallbackContext) -> int:
        """
        Шаг 2. Сохранение тикера в контекст, запрос суммы инвестиций
        """
        ticker: str = update.message.text.upper()
        context.user_data['ticker'] = ticker

        await update.message.reply_text(f"Ticker {ticker} accepted. Now enter the investment amount (in USD):")

        return AMOUNT

    @staticmethod
    async def get_amount(update: Update, context: CallbackContext) -> int:
        """
        Шаг 3. Запрос суммы и последующий запуск пайплайна:
            1) Получение исторических данных
            2) Обучение моделей
            3) Генерация прогноза
            4) Создание рекоммендаций
            5) Формирование графика
            6) Отправка результата пользователю
        """
        ticker = context.user_data['ticker']
        amount = float(update.message.text)
        if amount <= 0:
            await update.message.reply_text("Amount must be positive, please try again.")
            return AMOUNT
        try:
            # сообщение о начале обработки
            processing_started_message = await update.message.reply_text(
                f"Analyze stocks {ticker}.\n"
                f"Investment amount: ${amount:,.2f}.\n\n"
                "The process may take a few moments."
            )

            # 1) Получение исторических данных
            data = get_ticker_history(ticker)
            # 2) Обучение моделей
            best_model_name, best_model_info = train_models(data)
            # 3) Генерация прогноза
            forecast, current_price = generate_forecast(data, best_model_name, best_model_info)
            # 4) Создание рекоммендаций
            recommendations = calculate_trading_strategy(forecast, current_price, amount)
            # 5) Формирование графика
            forecast_plot = create_forecast_plot(data, forecast, ticker)
            # подготовка и форматирование ответа в формате html
            response = format_response(ticker, amount, best_model_name, best_model_info, recommendations)
            # логирование успешного запроса
            log_request(
                update.effective_user.id,
                ticker,
                amount,
                best_model_name,
                best_model_info['rmse'],
                recommendations['potential_profit']
            )
            # отправка ответа
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=forecast_plot,
                caption=response,
                parse_mode='HTML'
            )
            # удалаяется сообщение о начале обработки
            await processing_started_message.delete()

        except ValueError:
            # тикер не найден или данные недоступны
            await update.message.reply_text(
                f"Failed to retrieve data for ticker {ticker}"
                "Please check the ticker is correct and try again."
            )

            return ConversationHandler.END
        except Exception as e:
            # любая другая ошибка – логируем в файл и сообщаем об этом пользователю
            log_error(update.effective_user.id, e)
            await update.message.reply_text(
                "An error occurred while parsing. Please try again later or with different parameters."
            )

        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, _: CallbackContext) -> int:
        """
        Шаг 4. Обработка прерывания диалога пользователем
        """
        await update.message.reply_text('The operation has been cancelled.')

        return ConversationHandler.END
