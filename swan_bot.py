""" *************************************************
 * Title:					Main Script for trader*
 * Description:	Python script to integrate with mq5	*
 *						                            *
 * Author:                                Brian Obot*
 *						                            *
 * Purpose:					                        *
 *						                            *
 * Usage:	    For automated trading of forex on mq5*
 *						                            *
"""
print("Starting up RUNTIME environment...")
from queue import Queue
from datetime import datetime
import MetaTrader5 as mt5
import talib as ta
from talib import MA_Type
import pytz
from trader import Trader
from technqiues import get_MACD, get_RSI, RSI
from fortune_cards import candle_sticks
import time
print("Environment IMPORTS Completed!")


TIMEZONE = pytz.timezone('America/Araguaina') #if you do see this code....don't ask me how....all i know is that it works
TODAY_DAY = TIMEZONE.localize(datetime.now()).day

def still_today():
    #return bool value to show if today is still today
    today_day = TIMEZONE.localize(datetime.now()).day
    if today_day != TODAY_DAY:
        return False
    return True

def time_now():
    return TIMEZONE.localize(datetime.now())

def initialize():
    try:
        mt5.initialize()
    except:
        print('Initialization Unsuccessful...Possibly due to lack of internet connection or poor network')
        mt5.shutdown()
        return False, mt5.last_error()
    else:
        print("Initialization Successful")
        return True, time_now()
           
class Task():
    def __init__(self, trader):
        self.trader = trader
        self.task_id = trader.id

    def run(self):
        ''' the main trading actions block..to be rerun in a loop for all time validity of
            the program '''
        data = self.trader.get_data(time_now())
        l_data_time = data['time'].iloc[-1]

        #hack to visualize data latest time
        print(f'______latest_data_time______ = {l_data_time} ')
        print('__________DateTime___________ = {}'.format(time_now()))
        
        close_value = data['close']
        print('Current_close = {}'.format(close_value.iloc[-1]))
        candle_tales = self.trader.candle_stick_story(data, candle_sticks)

        rsi = get_RSI(close_value)
        macd = get_MACD(close_value)
        im_rsi = RSI(close_value, 4).iloc[-1]

        print('MAC-D value = [{}]'.format(macd))
        print("####################################")
        print(f"RSI Values looking Juicy.....{rsi}/ {im_rsi}")
        print("####################################")

        print(f"Sum of Candle sticks - {candle_tales[0]}")
        print(f"List of Candle sticks({len(candle_tales[1])})  - {candle_tales[1]}")
        
        if candle_tales[0] == 0:
            print('OH No ....i guess that was a false alert...well let\'s not give up')
                
        elif candle_tales[0] > 0:
            if int(rsi) <= 40:
                print('WOW.....About to place buy order...God\'s Grace')
                self.trader.place_buy_trade()
            else:
                print('OH No ....i guess that was a false alert...well let\'s not give up')

        elif candle_tales[0] < 0:
            if int(rsi) >= 60:
                print('WOW .....About to place sell order...God\'s Grace')
                self.trader.place_sell_trade()
            else:
                print('OH No ....i guess that was a false alert...well let\'s not give up')
        self.make_trade_decision(close_value)

    def make_trade_decision(self, close_value):
        print("Making trade decision here")

class TraderManager():
    def __init__(self, tasks=None):
        self.ready = Queue()
        if tasks:
            self.tasks = list(tasks)
        else:
            self.tasks = []
        for task in self.tasks:
            self.schedule(task) 

    def schedule(self, task):
        self.ready.put(task)

    def new(self, task):
        self.tasks.append(task)
        self.schedule(task)
        return self.tasks

    def mainloop(self):
        while True:
            task = self.ready.get()
            task.run()
            self.schedule(task)
            time.sleep(10)

class Lot(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lot = 0.1 #lot size

class Lottier(Trader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lot = 1.0 #lot size


if __name__ == "__main__":
    initialize() # use this function object to connect the script to the metatrader5 platform
    
    task_1 = Task(Trader(48593620))
    task_2 = Task(Lot(48593620))
    task_3 = Task(Lottier(48593620))

    engine = TraderManager()
    
    engine.new(task_1)
    engine.new(task_2)
    engine.new(task_3)
    
    engine.mainloop()




