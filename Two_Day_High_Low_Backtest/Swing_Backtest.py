from numpy import quantile, short
import pandas as pd
import time
import csv

def start_backtest(stock_name):
    
    t1 = time.time()
    
    stock_data = pd.read_csv(f"./Api_Fetched_Data/{stock_name}_fetched_data.csv")
    stock_data.drop(stock_data.columns[[0, 0]], axis=1, inplace=True)
    
    backtest_results = []
    
    long_position = False
    short_position = False
    
    initial_amount = 50000
    
    total_trades = 0
    sucessfull_trades = 0
    total_charges_paid = 0
    
    brokerage_charges = 0
    STT_percentage = 0.001
    transaction_charges_percentage = 0.0000345
    GST_percentage = 0.18
    stamp_duty_percentage = 0.00015
    
    long_side_stoploss = None
    short_side_stoploss = None
    
    long_trade = None
    short_trade = None
    
    stoploss_percentage = 0.02
    
    two_day_high = max(stock_data['High'][0], stock_data['High'][1])
    two_day_low = min(stock_data['Low'][0], stock_data['Low'][1])
    
    print(two_day_high, two_day_low)
    
    for i in range(2, len(stock_data)):
        
        high = stock_data['High'][i] * 1.0015
        low = stock_data['Low'][i] * 0.9985
        
        # print(stock_data['High'][i], stock_data['Low'][i])
        
        # square off short position
        if short_position and (high >= two_day_high or high >= short_side_stoploss):
            
            short_trade['buytime'] = stock_data['Datetime'][i]
            short_trade['buyprice'] = min(short_side_stoploss, two_day_high)
            short_trade['buyvalue'] = short_trade['quantity'] * short_trade['buyprice']

            # Charges #
            
            brokerage = 2 * brokerage_charges
            stt = short_trade['buyvalue'] * STT_percentage + short_trade['sellvalue'] * STT_percentage
            transaction_charge = short_trade['buyvalue'] * transaction_charges_percentage + short_trade['sellvalue'] * transaction_charges_percentage
            stamp_duty = short_trade['buyvalue'] * stamp_duty_percentage + short_trade['sellvalue'] * stamp_duty_percentage
            gst = (brokerage + transaction_charge) * GST_percentage
            
            total_charges = brokerage + stt + transaction_charge + stamp_duty + gst
            total_charges_paid = total_charges_paid + total_charges
            
            # Charges #
               
            short_trade['pnl'] = short_trade['sellvalue'] - short_trade['buyvalue'] - total_charges
            short_trade['success'] = short_trade['pnl'] >= 0
            short_trade['charges'] = total_charges
            
            initial_amount = initial_amount + short_trade['pnl']
            short_trade['closing_balance'] = initial_amount
            
            if short_trade['success']:
                sucessfull_trades = sucessfull_trades + 1
                
            backtest_results.append(short_trade)
            short_trade = None
            short_position = False
            
        # square off long position
        if long_position and (low <= two_day_low or low <= long_side_stoploss):
            
            long_trade['selltime'] = stock_data['Datetime'][i]
            long_trade['sellprice'] = max(long_side_stoploss, two_day_low)
            long_trade['sellvalue'] = long_trade['quantity'] * long_trade['sellprice']

            # Charges #
            
            brokerage = 2 * brokerage_charges
            stt = long_trade['buyvalue'] * STT_percentage + long_trade['sellvalue'] * STT_percentage
            transaction_charge = long_trade['buyvalue'] * transaction_charges_percentage + long_trade['sellvalue'] * transaction_charges_percentage
            stamp_duty = long_trade['buyvalue'] * stamp_duty_percentage + long_trade['sellvalue'] * stamp_duty_percentage
            gst = (brokerage + transaction_charge) * GST_percentage
            
            total_charges = brokerage + stt + transaction_charge + stamp_duty + gst
            total_charges_paid = total_charges_paid + total_charges
            
            # Charges #
               
            long_trade['pnl'] = long_trade['sellvalue'] - long_trade['buyvalue'] - total_charges
            long_trade['success'] = long_trade['pnl'] >= 0
            long_trade['charges'] = total_charges
            
            initial_amount = initial_amount + long_trade['pnl']
            long_trade['closing_balance'] = initial_amount
            
            if long_trade['success']:
                sucessfull_trades = sucessfull_trades + 1
                
            backtest_results.append(long_trade)
            long_trade = None
            long_position = False
            
        
        # create long position
        if high >= two_day_high and not long_position and not short_position:
            
            quantity = 1
            
            long_trade = {
                'buytime' : stock_data['Datetime'][i],
                'buyprice' : two_day_high,
                'quantity' : quantity,
                'buyvalue' : quantity * float(two_day_high),
                'opening_balance' : initial_amount
            }
            
            long_side_stoploss = long_trade['buyprice'] * (1 - stoploss_percentage)
            
            total_trades = total_trades + 1
            long_position = True
        
        # create short position
        if low <= two_day_low and not short_position and not long_position:
            
            quantity = 1
            
            short_trade = {
                'selltime' : stock_data['Datetime'][i],
                'sellprice' : two_day_low,
                'quantity' : quantity,
                'sellvalue' : quantity * float(two_day_low),
                'opening_balance' : initial_amount
            }
            
            short_side_stoploss = short_trade['sellprice'] * (1 + stoploss_percentage)
            
            total_trades = total_trades + 1
            short_position = True
        
        two_day_high = max(stock_data['High'][i - 1], stock_data['High'][i])
        two_day_low = min(stock_data['Low'][i - 1], stock_data['Low'][i])
    
    data_file = open(f'./Two_Day_High_Low_Backtest/Backtest_Results/Swing/{stock_name}_Swing_Backtest_Results.csv', 'w', newline='')       
    data_list = csv.DictWriter(data_file, fieldnames = [
        'buytime', 
        'selltime', 
        'buyprice', 
        'sellprice', 
        'quantity', 
        'buyvalue', 
        'sellvalue', 
        'opening_balance', 
        'closing_balance', 
        'pnl', 
        'charges',
        'success'
    ])
    
    data_list.writeheader()
    data_list.writerows(backtest_results)
    
    print('Total no of trades: ', total_trades)
    print('Sucessfull trades: ', sucessfull_trades)
    
    if total_trades:
        print('Accuracy: ', (sucessfull_trades / total_trades) * 100, '%')
    
    print('Total Charges Paid: ', total_charges_paid)
    print('Final closing balance: ', initial_amount)
    
    t2 = time.time()
    print('Your Backtest took', t2 - t1, 's to execute')   