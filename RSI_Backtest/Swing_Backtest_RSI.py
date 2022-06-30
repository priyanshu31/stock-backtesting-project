from numpy import true_divide
import pandas as pd
import time
import csv

def start_backtest(stock_name):
    
    t1 = time.time()
    
    stock_data_file = open(f'./RSI_Backtest/Data_with_RSI/{stock_name}_data_with_rsi.csv')
    stock_data = csv.DictReader(stock_data_file)
    
    backtest_results = []
    
    long_position = False
    oversold_rsi_value = 30
    intial_amount = 10000
    
    stoploss_percentage = 0.96
    target_percentage = 1.08
    stoploss = None
    target = None
    previous_rsi = None
    trade = None
    
    total_trades = 0
    sucessfull_trades = 0
    total_charges_paid = 0
    
    brokerage_charges = 0
    STT_percentage = 0.001
    transaction_charges_percentage = 0.0000345
    GST_percentage = 0.18
    stamp_duty_percentage = 0.00015
    
    for row in stock_data: 
    
        if row['RSI_Close'] == 'nan' or row['RSI_Close'] == '':
            continue
        
        rsi = float(row['RSI_Close'])
        
        if previous_rsi and not long_position and rsi <= previous_rsi and rsi <= oversold_rsi_value:
            
            quantity = int(intial_amount / float(row['Close']))
            
            trade = {
                'buytime' : row['Datetime'],
                'buyprice' : float(row['Close']),
                'quantity' : quantity,
                'buyvalue' : quantity * float(row['Close']),
                'opening_balance' : intial_amount
            }
            
            stoploss = trade['buyprice'] * stoploss_percentage
            target = trade['buyprice'] * target_percentage
            
            total_trades = total_trades + 1
            long_position = True
            
            continue
            
        if long_position and stoploss >= float(row['Low']):
            
            trade['selltime'] = row['Datetime']
            trade['sellprice'] = stoploss - 0.1
            trade['sellvalue'] = trade['quantity'] * trade['sellprice']
            
            # Charges #
            
            brokerage = 2 * brokerage_charges
            stt = trade['buyvalue'] * STT_percentage + trade['sellvalue'] * STT_percentage
            transaction_charge = trade['buyvalue'] * transaction_charges_percentage + trade['sellvalue'] * transaction_charges_percentage
            stamp_duty = trade['buyvalue'] * stamp_duty_percentage + trade['sellvalue'] * stamp_duty_percentage
            gst = (brokerage + transaction_charge) * GST_percentage
            
            total_charges = brokerage + stt + transaction_charge + stamp_duty + gst
            total_charges_paid = total_charges_paid + total_charges
            
            # Charges #
            
            trade['pnl'] = trade['sellvalue'] - trade['buyvalue'] - total_charges
            trade['success'] = trade['pnl'] > 0
            trade['charges'] = total_charges
            
            intial_amount = intial_amount + trade['pnl']
            trade['closing_balance'] = intial_amount
            
            if trade['success']:
                sucessfull_trades = sucessfull_trades + 1
                
            backtest_results.append(trade)
            trade = None
            long_position = False
            
            continue
        
        if long_position and target <= float(row['High']):
            
            stoploss = float(row['High']) * stoploss_percentage
            target = stoploss * target_percentage
            
            continue
        
        previous_rsi = rsi
     
    data_file = open(f'./RSI_Backtest/Backtest_Results/Swing/{stock_name}_Swing_Backtest_Results_RSI.csv', 'w', newline='')       
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
    print('Final closing balance: ', intial_amount)
    
    t2 = time.time()
    print('Your Backtest took', t2 - t1, 's to execute')     

# start_backtest()