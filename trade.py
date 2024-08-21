from trader import Trader

from mt5 import Account
from mt5.account import create_test_account


def main():
    test_account = create_test_account()
    test_trader = Trader(test_account)

    test_trader.run()


if __name__ == "__main__":
    count = 0
    while count <= 100000000000000000000000000:
        main()
        count += 1