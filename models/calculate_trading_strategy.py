import math
from statistics import mean
from typing import Dict, List


def calculate_trading_strategy(
        forecast: List[float],
        current_price: float,
        amount: float,
) -> Dict[str, object]:
    """
    Оценка торговой стратегии по прогнозу цен

    :param forecast: список прогнозируемых цен
    :param current_price: текущая цена актива
    :param amount: сумма потенциальных вложений

    :return словарь с информацией о прогнозе
    """
    if not forecast:
        raise ValueError("forecast list must not be empty")

    #  ожидаемое изменение в процентах (рост/падение) относительно текущей цены.
    price_change_percent = ((mean(forecast) - current_price) / current_price) * 100

    # экстремумы цен и их дни
    min_price = min(forecast)
    max_price = max(forecast)
    buy_day = forecast.index(min_price) + 1
    sell_day = forecast.index(max_price) + 1

    # количество акций, которые можно купить за заданную сумму (с округлением вниз, чтобы не выйти за заданную сумму)
    shares = math.floor(amount / current_price)
    # потенциальная прибыль
    potential_profit = shares * (max_price - current_price)
    roi = (potential_profit / amount) * 100 if amount else 0.0

    return {
        "current_price": current_price,
        "price_change_percent": price_change_percent,
        "min_forecast_price": min_price,
        "buy_day": buy_day,
        "max_forecast_price": max_price,
        "sell_day": sell_day,
        "potential_profit": potential_profit,
        "roi": roi,
    }
