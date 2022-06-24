from numpy import datetime64, short, square, true_divide
import pandas as pd
import time
import csv
import datetime

def start_backtest(stock_name):
    
    t1 = time.time()
    
    stock_data_file = open(f'./RSI_Backtest/Data_with_RSI/{stock_name}_data_with_rsi.csv')
    stock_data = csv.DictReader(stock_data_file)
    
    backtest_results = []
    
    long_position = False
    short_position = False    
    oversold_rsi_value = 20
    overbought_rsi_value = 80
    intial_amount = 10000
    leverage = 20
    
    stoploss_percentage = 0.005
    target_percentage = 0.01
    stoploss = None
    target = None
    previous_rsi = None
    trade = None
    
    total_trades = 0
    sucessfull_trades = 0
    total_charges_paid = 0
    
    brokerage_charges = 20
    STT_percentage = 0.00025
    transaction_charges_percentage = 0.0000345
    GST_percentage = 0.18
    stamp_duty_percentage = 0.00003
    
    Intraday_position_squareoff_time = datetime.time(15, 9, 0)
    
    for row in stock_data: 
    
        Datetime = datetime.datetime.fromisoformat(row['Datetime'])
        
        if Datetime.time() > Intraday_position_squareoff_time:
            continue
        
        if row['RSI_Close'] == 'nan' or row['RSI_Close'] == '':
            continue
        
        rsi = float(row['RSI_Close'])
        
        if previous_rsi and not short_position and not long_position and intial_amount > 0 and rsi <= previous_rsi and rsi <= oversold_rsi_value:
            
            quantity = int(intial_amount / (float(row['Close']) / leverage))
            
            trade = {
                'buytime' : row['Datetime'],
                'buyprice' : float(row['Close']),
                'quantity' : quantity,
                'buyvalue' : quantity * float(row['Close']),
                'opening_balance' : intial_amount
            }
            
            stoploss = trade['buyprice'] * (1 - stoploss_percentage)
            target = trade['buyprice'] * (1 + target_percentage)
            
            total_trades = total_trades + 1
            long_position = True
            
        if long_position and target <= float(row['High']):
            
            stoploss = float(row['High']) * (1 - stoploss_percentage)
            target = stoploss * (1 + target_percentage)
            
        if long_position and (stoploss >= float(row['Low']) or Intraday_position_squareoff_time == Datetime.time()):
            
            trade['selltime'] = row['Datetime']
            trade['sellprice'] = stoploss - 0.1
            trade['sellvalue'] = trade['quantity'] * trade['sellprice']
            
            # Charges #
            
            brokerage = 2 * brokerage_charges
            stt = trade['sellvalue'] * STT_percentage
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
            
        if previous_rsi and not long_position and not short_position  and intial_amount > 0 and rsi >= previous_rsi and rsi >= overbought_rsi_value:
            
            quantity = int(intial_amount / (float(row['Close']) / leverage))
            
            trade = {
                'selltime' : row['Datetime'],
                'sellprice' : float(row['Close']),
                'quantity' : quantity,
                'sellvalue' : quantity * float(row['Close']),
                'opening_balance' : intial_amount
            }
            
            stoploss = trade['sellprice'] * (1 + stoploss_percentage)
            target = trade['sellprice'] * (1 - target_percentage)
            
            total_trades = total_trades + 1
            short_position = True
            
        if short_position and target >= float(row['Low']):
            
            stoploss = float(row['Low']) * (1 + stoploss_percentage)
            target = stoploss * (1 - target_percentage)
            
        if short_position and (stoploss <= float(row['High']) or Intraday_position_squareoff_time == Datetime.time()):
            
            trade['buytime'] = row['Datetime']
            trade['buyprice'] = stoploss + 0.1
            trade['buyvalue'] = trade['quantity'] * trade['buyprice']
            
            # Charges #
            
            brokerage = 2 * brokerage_charges
            stt = trade['sellvalue'] * STT_percentage
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
            short_position = False
        
        
        previous_rsi = rsi
     
    data_file = open(f'./RSI_Backtest/Backtest_Results/Intraday/{stock_name}_Intraday_Backtest_Results_RSI.csv', 'w', newline='')       
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

# start_backtest('NIFTY')