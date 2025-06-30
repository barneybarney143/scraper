import pandas as pd

from ema_crossover import get_signal


def test_get_signal_buy():
    w = pd.DataFrame({"ema_fast": [2], "ema_slow": [1]})
    d = pd.DataFrame({"Close": [10], "sma200": [9]})
    assert get_signal(w, d) == "BUY"


def test_get_signal_sell():
    w = pd.DataFrame({"ema_fast": [1], "ema_slow": [2]})
    d = pd.DataFrame({"Close": [8], "sma200": [9]})
    assert get_signal(w, d) == "SELL"


def test_get_signal_hold():
    w = pd.DataFrame({"ema_fast": [1.5], "ema_slow": [1.5]})
    d = pd.DataFrame({"Close": [8], "sma200": [9]})
    assert get_signal(w, d) == "HOLD"
