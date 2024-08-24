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

from trader import Trader

from mt5 import Account
from mt5.account import create_test_account


def main() -> None:
    test_account = create_test_account()
    test_trader = Trader(test_account)

    test_trader.run()


if __name__ == "__main__":
    count = 0
    while count <= 10:
        main()
        count += 1
