import traceback
from datetime import datetime

log_file = "logs.txt"


def log_request(user_id, ticker, amount, best_model, best_metric, profit):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()}|{user_id}|{ticker}|{amount}|{best_model}|{best_metric:.4f}|{profit:.2f}\n")


def log_error(user_id, error: Exception):
    tb = traceback.format_exc()
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()}|{user_id}|ERROR|{error}|Traceback: {tb}\n")
