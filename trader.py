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
import pandas as pd
import MetaTrader5 as mt5

DEV_MODE = True #REMEMBER to deactivate when deploying for use

class Trader:
    def __init__(self, account, symbol='EURUSD'):
        self.id = "Brian's Trader Instance"
        self.account = account
        self.symbol =  symbol #symbol to be used...
        self.lot = 0.01 #lot size
        self.deviation = 20 #
        self.timeframe = mt5.TIMEFRAME_M1 #timeframe....one minute is recommended for the power of this project
        self.trades = {}
        self.gains = {}
        print(f"Trader instance has been created with following settings: \n[ACCOUNT_NUMBER]: {self.account}\n[SYMBOL]: {self.symbol}\n[LOT_SIZE]: {self.lot}")

    def login(self, account: str) -> bool:
        '''method to login to specified account number'''
        if mt5.login(self.account):
            print(f'CONNECTED to [{account}]')
            return True
        else:
            print(f'FAILED to CONNECT to [{account}]')
            return False
        
    def get_account_info() -> dict:
        info = mt5.account_info()._asdict()
        print(f"🌷🌷🌷🌷🌷🌷🌷🌷🌷🌷🌷 {info = }")

    def setup_buyRequest(self):
        symbol_info = mt5.symbol_info(self.symbol)
        point = symbol_info.point
        price_buy = mt5.symbol_info_tick(self.symbol).ask 

        request_buy = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price_buy,
            #"sl": price_buy - 5 * point,
            "tp": price_buy + (5 * point) ,
            "deviation": 20,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN, }

        return request_buy

    def setup_sellRequest(self):
        symbol_info = mt5.symbol_info(self.symbol)
        point = symbol_info.point
        price_sell = mt5.symbol_info_tick(self.symbol).bid 

        request_sell = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price_sell,
            #"sl" : price_sell + 5 * point,
            "tp": price_sell - (5 * point) ,
            "deviation": 20,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN, }

        return request_sell

    def get_data(self, current_time, count=1000):
        rates = mt5.copy_rates_from(self.symbol, self.timeframe, current_time , count)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        if DEV_MODE:
            df.to_csv("data_sample.csv") # use to save df to a local file
        return df

    def candle_stick_story(self, data, candles):
        open_ = data['open']
        high = data['high']
        low = data['low']
        close = data['close']

        table = pd.DataFrame()

        #refactor this loops and ensure it truthiness
        for value in (candles):
            table[value] = candles[value](open_, high, low, close)
        
        if DEV_MODE:
            table.to_csv("candle_history.csv") # use to save df to a local file

        df_1 = table[:]

        active_candlestick = []
        active_columns_value = []

        for n in df_1.columns:
            lv = df_1[n].iloc[-1]
            if lv != 0:
                active_candlestick.append(n)
                active_columns_value.append(lv)

        print(f'{len(active_candlestick)} Candlestick Pattern(s) found')

        candle_value = sum(active_columns_value)
        return candle_value, active_candlestick

    def place_buy_trade(self):
        request_buy = self.setup_buyRequest()
        result = mt5.order_send(request_buy)
        position_id = result.order
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(self.symbol, self.lot, request_buy["price"], self.deviation))
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('Trade Failed! retcode={}'.format(result.retcode))
            return False
        else:
            print("Trade Successful!...God's Grace!")
            return True

    def place_sell_trade(self):
        request_sell = self.setup_sellRequest()
        result = mt5.order_send(request_sell)
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(self.symbol, self.lot, request_sell["price"], self.deviation))
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('Trade Failed! retcode={}'.format(result.retcode))
            return False
        else:
            print("Trade Successful!...God's Grace!")
            return True


print('trader module loaded Sucessfully!')



