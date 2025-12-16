import io

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter


def create_forecast_plot(
        data: pd.DataFrame,
        forecast: list[float],
        ticker: str,
) -> io.BytesIO:
    """
    Генерация png‑изображение графика цены акции:
    - ось X – даты (исторические + прогнозируемые)
    - ось Y – цены

    :param ticker: тикер, для которого строиться график
    :param forecast: предсказания
    :param data: датафрейм на основе которого будет строиться график
    :return объект BytesIO с изображением
    """
    last_date = data.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=len(forecast),
        freq="D",
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        data.index,
        data["Close"],
        label="Historical",
        color="#2ca02c",
        linewidth=2,
    )

    ax.plot(
        future_dates,
        forecast,
        label="Forecast",
        color="#ff7f0e",
        linewidth=2,
        linestyle="--",
    )

    ax.set_title(f"Forecast for {ticker.upper()}", fontsize=14, weight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)

    # сохраняем график в буфер памяти в формате png
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return buf
