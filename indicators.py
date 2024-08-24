import talib as ta
import pandas as pd
import numpy as np


def get_RSI(x, timeperiod=4):
    rsi = ta.RSI(x, timeperiod)
    return rsi.iloc[-1]


def get_MACD(x, timeperiod=14):
    macd = ta.MACD(x, timeperiod)
    # return macd[0], macd[1], macd[2]
    return "MACD Coming soon!"


def RSI(series, period):
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period - 1]] = np.mean(u[:period])  # first value is sum of avg gains
    u = u.drop(u.index[: (period - 1)])
    d[d.index[period - 1]] = np.mean(d[:period])  # first value is sum of avg losses
    d = d.drop(d.index[: (period - 1)])
    rs = (
        pd.DataFrame.ewm(u, com=period - 1, adjust=False).mean()
        / pd.DataFrame.ewm(d, com=period - 1, adjust=False).mean()
    )
    return 100 - 100 / (1 + rs)
