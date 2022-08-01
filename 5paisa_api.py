from decouple import config
from py5paisa import FivePaisaClient
import pandas
import time
import json
from RSI_Backtest import Intraday_Backtest_RSI, RSI_Calculater, Swing_Backtest_RSI
from EMA_Backtest import EMA_Calculater, Intraday_Backtest_EMA
from Two_Day_High_Low_Backtest import Swing_Backtest

t1 = time.time()

# TODO: Kindly add 5paisa account details in .env for api working
# 5paisa Authentication #

email = config('5PAISA_EMAIL')
pwd = config('5PAISA_PASSWORD')
dob = config('5PAISA_DOB')

cred = {
    "APP_NAME": config('APP_NAME'),
    "APP_SOURCE": config('APP_SOURCE'),
    "USER_ID": config('USER_ID'),
    "PASSWORD": config('PASSWORD'),
    "USER_KEY": config('USER_KEY'),
    "ENCRYPTION_KEY": config('ENCRYPTION_KEY')
}

client = FivePaisaClient(email=email, passwd=pwd, dob=dob,cred=cred)
client.login()

# 5paisa Authentication #

# scripcode loading #

json_scripcode_file = open('./ScripCodes/new-scripcode-json.json')
json_scripcode_data = json.load(json_scripcode_file)

stock_name = 'BANKNIFTY'
scripcode = json_scripcode_data[stock_name]['Scripcode']

# scripcode loading #

# Data Fetching and Storing #

df=pandas.DataFrame(client.historical_data('N','C',scripcode,'1d','2017-01-01','2022-08-01'))
# print(df)

df.to_csv(f"./Api_Fetched_Data/{stock_name}_fetched_data.csv")
# Data Fetching and Storing #

t2 = time.time()
print('Your API fetching took', t2 - t1, 's to execute')

# # RSI Backtest #

# RSI_Calculater.calculate_RSI(stock_name)
# Swing_Backtest_RSI.start_backtest(stock_name)
# Intraday_Backtest_RSI.start_backtest(stock_name)
# print('\n')

# # RSI Backtest #

# EMA Backtest #

# small_timeperiod = 20
# large_timeperiod = 50

# EMA_Calculater.calculate_EMA(stock_name, small_timeperiod, large_timeperiod)
# Intraday_Backtest_EMA.start_backtest(stock_name, small_timeperiod, large_timeperiod)
# print('\n')

# EMA Backtest #

# Two Day High Low Backtest

Swing_Backtest.start_backtest(stock_name)

# Two Day High Low Backtest

t3 = time.time()
print('Total Execution Time: ', t3 - t1, 's')

