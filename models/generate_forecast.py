import numpy as np
import pandas as pd


def generate_forecast(
        data: pd.DataFrame,
        best_model_name: str,
        best_model_info: dict,
        horizon: int = 30,
) -> tuple[list[float], float]:
    """
    Генерация прогноза цены акции.

    :param data: датафрейм с историческими данными, должен иметь колонку «Close» (текущая цена)
    :param best_model_name: название модели
    :param best_model_info: словарь с уже обученными моделями
    :param horizon: количество дней с прогнозируемой ценой, по умолчанию, 30
    :return: кортеж (список прогнозируемых цен, текущая цена последнего наблюдения).
    """
    current_price = float(data["Close"].iloc[-1])
    best_model = best_model_info["model"]
    if best_model_name == "RandomForest":
        # прогнозируется с помощью скользящего окна из 5 лагов
        lags = 5
        recent = data["Close"].iloc[-lags:].values

        forecast = []
        for _ in range(horizon):
            features = pd.DataFrame(
                [recent],
                columns=[f"lag_{i + 1}" for i in range(lags)],
            )
            # прогноз в точке
            prediction = float(best_model.predict(features)[0])
            forecast.append(prediction)

            # сдвиг окна
            recent = np.roll(recent, -1)
            recent[-1] = prediction

        return forecast, current_price

    if best_model_name == "ARIMA":
        predictions = best_model.forecast(steps=horizon)
        forecast = predictions.tolist()

        return forecast, current_price

    if best_model_name == "LSTM":
        window = 30
        if len(data) < window:
            raise ValueError("Not enough historical data to generate forecast")

        recent = data["Close"].iloc[-window:].values.reshape(1, window, 1)

        forecast = []
        for _ in range(horizon):
            prediction = float(best_model.predict(recent)[0, 0])
            forecast.append(prediction)
            recent = np.append(recent[:, 1:, :], [[prediction]], axis=1)

        return forecast, current_price

    raise ValueError(f"Unsupported model: {best_model_name}")
