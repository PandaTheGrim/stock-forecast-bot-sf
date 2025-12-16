from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential


def _prepare_lag_features(df: pd.DataFrame, lags: int = 5) -> pd.DataFrame:
    """
    Создание лаговых признаков для случайного леса:
    - добавляет столбцы lag_1 … lag_{lags}
    - удаляет строки с пропущенными значениями

    :param df: датафрейм
    :param lags: число лагов
    :return: датафрейм с лаговыми признаками
    """
    df_with_lags = df.copy()
    for i in range(1, lags + 1):
        df_with_lags[f'lag_{i}'] = df_with_lags['Close'].shift(i)

    df_with_lags.dropna(inplace=True)

    return df_with_lags


def _train_random_forest(df_with_lags: pd.DataFrame) -> tuple[RandomForestRegressor, Any]:
    """
    Обучение случайного леса:

    :param df_with_lags: датафрейм с лаговыми признаками
    :return: (обученная модель, rmse)
    """
    x = df_with_lags.drop(columns='Close')
    y = df_with_lags['Close']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False)
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(x_train, y_train)
    predicted_value = model.predict(x_test)
    rmse = np.sqrt(mean_squared_error(y_test, predicted_value))

    return model, rmse


def _train_arima(series: pd.Series, order=(5, 1, 0)):
    """
    Обучение модели ARIMA: обучение происходит по всей выборке, а оценка RMSE на последних 20% данных

    :param series: серия цен
    :param order: порядок ARIMA (p, d, q)
    :return: (обученная модель, rmse)
    """
    fitted_model = ARIMA(series, order=order).fit()
    train_size = int(len(series) * 0.8)
    value_series = series.iloc[train_size:]

    predictions = fitted_model.predict(start=train_size, end=len(series) - 1, typ='levels')
    rmse = np.sqrt(mean_squared_error(value_series, predictions))

    return fitted_model, rmse


def _train_lstm(series: pd.Series, window: int = 30, epochs: int = 40):
    """
    Обучение модели LSTM:
    - формирует скользящее окно заданной длины
    - разделяет данные на train/test без перемешивания

    :param series: серия цен
    :param window: размер окна (число дней)
    :param epochs: максимальное число эпох
    :return: (обученная модель, rmse)
    """
    x, y = [], []
    for i in range(len(series) - window):
        x.append(series.iloc[i:i + window].values)
        y.append(series.iloc[i + window])

    x = np.array(x)
    y = np.array(y)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, shuffle=False
    )

    model = Sequential([
        LSTM(32, activation='tanh', input_shape=(window, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    es = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    model.fit(
        x_train[..., None],
        y_train,
        epochs=epochs,
        batch_size=16,
        validation_data=(x_test[..., None], y_test),
        callbacks=[es],
        verbose=0
    )

    predicted_value = model.predict(x_test[..., None]).flatten()
    rmse = np.sqrt(mean_squared_error(y_test, predicted_value))

    return model, rmse


def train_models(data: pd.DataFrame):
    """
    Обучение трёх моделей и выбор лучшей - с наименьшим RMSE

    :param data: датафрейм
    :return: (имя лучшей модели, словарь {'model': модель, 'rmse': значение})
    """
    df_with_lags = _prepare_lag_features(data, lags=5)
    rf_model, rf_rmse = _train_random_forest(df_with_lags)
    arima_model, arima_rmse = _train_arima(data['Close'])
    lstm_model, lstm_rmse = _train_lstm(data['Close'])

    all_models = {
        'RandomForest': (rf_model, rf_rmse),
        'ARIMA': (arima_model, arima_rmse),
        'LSTM': (lstm_model, lstm_rmse),
    }

    # модель с наименьшим RMSE
    best_name = min(all_models, key=lambda k: all_models[k][1])
    best_model, best_rmse = all_models[best_name]

    best_model_info = {
        'rmse': best_rmse,
        'model': best_model
    }

    return best_name, best_model_info
