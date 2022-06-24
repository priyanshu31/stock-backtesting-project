import talib
import pandas as pd
import time

def calculate_RSI(stock_name):
    t1 = time.time()

    stock_data = pd.read_csv(f"./Api_Fetched_Data/{stock_name}_fetched_data.csv")
    final_stock_data = stock_data.to_numpy()
    open_price = final_stock_data[:, 2].astype('double')
    high_price = final_stock_data[:, 3].astype('double')
    low_price = final_stock_data[:, 4].astype('double')
    close_price = final_stock_data[:, 5].astype('double')

    RSI_Open_Data = talib.RSI(open_price, timeperiod=14)
    RSI_High_Data = talib.RSI(high_price, timeperiod=14)
    RSI_Low_Data = talib.RSI(low_price, timeperiod=14)
    RSI_Close_Data = talib.RSI(close_price, timeperiod=14)

    # To remove unnamed column of serial number 
    # print(stock_data)
    stock_data.drop(stock_data.columns[[0, 0]], axis=1, inplace=True)
    # print(stock_data)

    stock_data['RSI_Open'] = RSI_Open_Data
    stock_data['RSI_High'] = RSI_High_Data
    stock_data['RSI_Low'] = RSI_Low_Data
    stock_data['RSI_Close'] = RSI_Close_Data

    stock_data.to_csv(f'./RSI_Backtest/Data_with_RSI/{stock_name}_data_with_rsi.csv')

    t2 = time.time()
    print('Your RSI Calculation took', t2 - t1, 's to execute')
    
# calculate_RSI()