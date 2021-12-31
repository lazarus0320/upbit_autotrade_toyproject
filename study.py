import pyupbit
import datetime

# access = "E0I9cDOUy8vbOeFeFkXs4WTWpaFA8PxhQsQWekKu"
# secret = "T6XxX8pBZSeo4xSaU12WQWSxXCpBTlAwUdJ9Sxx8"

# upbit = pyupbit.Upbit(access, secret)
# print(upbit.get_balance())
ticker = "KRW-BTC"
buy_time = datetime.datetime.now()
print(type(buy_time))
value = 500000
print(f"{buy_time}  {ticker}  평단 : {value:,}  매수 금액 : 5000원")