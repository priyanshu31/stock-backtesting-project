import talib
import pandas as pd
import time

def calculate_EMA(stock_name, small_timeperiod, large_timeperiod):
    t1 = time.time()

    stock_data = pd.read_csv(f"./Api_Fetched_Data/{stock_name}_fetched_data.csv")
    final_stock_data = stock_data.to_numpy()
    open_price = final_stock_data[:, 2].astype('double')
    high_price = final_stock_data[:, 3].astype('double')
    low_price = final_stock_data[:, 4].astype('double')
    close_price = final_stock_data[:, 5].astype('double')


    # To remove unnamed column of serial number 
    # print(stock_data)
    stock_data.drop(stock_data.columns[[0, 0]], axis=1, inplace=True)
    # print(stock_data)

    # 50 EMA Calculation #
    
    EMA_Open_Data = talib.EMA(open_price, timeperiod=small_timeperiod)
    EMA_High_Data = talib.EMA(high_price, timeperiod=small_timeperiod)
    EMA_Low_Data = talib.EMA(low_price, timeperiod=small_timeperiod)
    EMA_Close_Data = talib.EMA(close_price, timeperiod=small_timeperiod)
    
    stock_data[f'EMA_Open_{small_timeperiod}'] = EMA_Open_Data
    stock_data[f'EMA_High_{small_timeperiod}'] = EMA_High_Data
    stock_data[f'EMA_Low_{small_timeperiod}'] = EMA_Low_Data
    stock_data[f'EMA_Close_{small_timeperiod}'] = EMA_Close_Data

    # 50 EMA Calculation #
    
    # 200 EMA Calculation #

    EMA_Open_Data = talib.EMA(open_price, timeperiod=large_timeperiod)
    EMA_High_Data = talib.EMA(high_price, timeperiod=large_timeperiod)
    EMA_Low_Data = talib.EMA(low_price, timeperiod=large_timeperiod)
    EMA_Close_Data = talib.EMA(close_price, timeperiod=large_timeperiod)
    
    stock_data[f'EMA_Open_{large_timeperiod}'] = EMA_Open_Data
    stock_data[f'EMA_High_{large_timeperiod}'] = EMA_High_Data
    stock_data[f'EMA_Low_{large_timeperiod}'] = EMA_Low_Data
    stock_data[f'EMA_Close_{large_timeperiod}'] = EMA_Close_Data

    # 200 EMA Calculation #
    
    stock_data.to_csv(f'./EMA_Backtest/Data_with_EMA/{stock_name}_data_with_ema.csv')

    t2 = time.time()
    print('Your EMA Calculation took', t2 - t1, 's to execute')
    