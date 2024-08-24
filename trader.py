""" *************************************************
 * Title:					     Module for Swan_bot*
 * Description:	Python script to integrate with mq5	*
 *						                            *
 * Author:                                Brian Obot*
 *						                            *
 * Purpose:					                        *
 *						                            *
 * Usage:	    For automated trading of forex on mq5*
 *						                            *
"""
import pytz
import logging
import indicators
import pandas as pd
import MetaTrader5 as mt5

from fortune_cards import candle_sticks
from datetime import datetime
from mt5 import Account, TraderOrder

DEBUG = True
TIMEZONE = pytz.timezone('America/Araguaina')

logging.basicConfig(filename="logs", filemode="w", format="%(name)s → %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class Trader:
    """
    The trader class controls an account and decides on the actions to be perform on the account.
    """
    def __init__(
            self, 
            account: Account, 
            symbol='EURUSD', 
            lot: float = 0.01, 
            deviation: int = 20, 
            timeframe = mt5.TIMEFRAME_M1,
        ):
        self.account = account
        self.symbol = symbol
        self.lot = lot
        self.deviation = deviation
        self.timeframe = timeframe
        self.account.connect()
        account_info = self.account.info()
        
        logger.info("Trader Account Instantiated: ", account_info)

    def run(self) -> bool:
        market_data = self.get_data(self.__class__.localize_time())
        candle_tales = self.candle_stick_story(market_data, candle_sticks)

        close_price = market_data['close']

        rsi_value = indicators.get_RSI(close_price)
        macd_value = indicators.get_MACD(close_price)
        im_rsi_value = indicators.RSI(close_price, 4).iloc[-1]

        logging.debug("Close Price : %s", close_price)
        logging.debug("RSI Value   : %s", rsi_value)
        logging.debug("MACD Value  : %s", macd_value)
        logging.debug("IM RSI Value: %s", im_rsi_value)
        logging.debug("Candle tales: %s", candle_tales)

        candle_sum, candles = candle_tales
        logging.debug("Candle sum  : %s", candle_sum)
        logging.debug("Candles List: %s", candles)

        order = self.make_trade_decision(close_price, rsi_value, candle_sum)
        logging.debug("Order Created:  %s", order)

        return True

    def get_data(self, current_time, count=1000):
        rates = mt5.copy_rates_from(self.symbol, self.timeframe, current_time , count)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        if DEBUG:
            df.to_csv("data_sample.csv") # use to save df to a local file
        return df

    def candle_stick_story(self, data, candles) -> tuple[int, list]:
        """
        Return a tuple containing (candles_sum, [names of candles found])

        +ve candles_sum => 
        -ve candles_sum => 
        """
        open_ = data['open']
        high = data['high']
        low = data['low']
        close = data['close']

        table = pd.DataFrame()

        #refactor this loops and ensure it truthiness
        for value in (candles):
            table[value] = candles[value](open_, high, low, close)
        
        if DEBUG:
            table.to_csv("candle_history.csv") # use to save df to a local file

        df_1 = table[:]

        active_candlestick = []
        active_columns_value = []

        for n in df_1.columns:
            lv = df_1[n].iloc[-1]
            if lv != 0:
                active_candlestick.append(n)
                active_columns_value.append(lv)

        logging.debug('%s Candlestick Pattern(s) found', len(active_candlestick))

        candle_value = sum(active_columns_value)
        return candle_value, active_candlestick

    def make_trade_decision(self, price: float, rsi_value: float, candle_sum: float) -> list[TraderOrder]:
        orders = []
        order_1, order_2 = None, None
        # rsi based decision
        if rsi_value <= 20:
            order_1 = self.account.create_buy_order(self.symbol)
        elif rsi_value >= 80:
            order_1 = self.account.create_sell_order(self.symbol)
        
        # candle stick based decision
        if candle_sum > 0:
            order_2 = self.account.create_buy_order(self.symbol)
        elif candle_sum < 0:
            order_2 = self.account.create_sell_order(self.symbol)

        if order_1: orders.append(order_1)
        if order_2: orders.append(order_2)

        return orders
        
    @staticmethod
    def localize_time():
        return TIMEZONE.localize(datetime.now())


