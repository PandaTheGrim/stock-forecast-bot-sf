import pandas as pd
import yfinance


def get_ticker_history(ticker) -> pd.DataFrame:
    # используем для обучения данные за 2 года
    data = yfinance.Ticker(ticker).history(period='2y')
    if data.empty:
        raise ValueError(f'No data for ticker {ticker}')

    data = data[['Close']].copy()
    data.index = pd.to_datetime(data.index)

    return data