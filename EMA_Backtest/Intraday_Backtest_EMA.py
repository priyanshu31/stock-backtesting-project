from numpy import datetime64, short, square, true_divide
import pandas as pd
import time
import csv
import datetime

def start_backtest(stock_name, small_timeperiod, large_timeperiod):
    
    t1 = time.time()
    
    stock_data_file = open(f'./EMA_Backtest/Data_with_EMA/{stock_name}_data_with_ema.csv')
    stock_data = csv.DictReader(stock_data_file)
    
    backtest_results = []
    
    long_position = False
    short_position = False    
    intial_amount = 10000
    leverage = 5
    
    stoploss_percentage = 0.0025
    target_percentage = 0.0025
    stoploss = None
    target = None
    previous_ema_small_1 = None
    previous_ema_small_2 = None
    previous_ema_large_1 = None
    previous_ema_large_2 = None
    
    trade = None
    
    total_trades = 0
    sucessfull_trades = 0
    total_charges_paid = 0
    
    brokerage_charges = 20
    STT_percentage = 0.00025
    transaction_charges_percentage = 0.0000345
    GST_percentage = 0.18
    stamp_duty_percentage = 0.00003
    
    ema_small_key_name = f'EMA_Close_{small_timeperiod}'    
    ema_large_key_name = f'EMA_Close_{large_timeperiod}'    
    
    Intraday_position_squareoff_time = datetime.time(15, 9, 0)
    
    for row in stock_data: 
    
        Datetime = datetime.datetime.fromisoformat(row['Datetime'])
        
        if Datetime.time() > Intraday_position_squareoff_time or row[ema_large_key_name] == '' or row[ema_small_key_name] == '':
            continue
        
        ema_small = float(row[ema_small_key_name])
        ema_large = float(row[ema_large_key_name])
        
        if not previous_ema_large_1 or not previous_ema_large_2 or not previous_ema_small_1 or not previous_ema_small_2:
            
            previous_ema_small_2 = previous_ema_small_1
            previous_ema_small_1 = ema_small
            previous_ema_large_2 = previous_ema_large_1
            previous_ema_large_1 = ema_large
            continue
        
        
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
            
        if long_position and target <= float(row['High']):
            
            stoploss = float(row['High']) * (1 - stoploss_percentage)
            target = stoploss * (1 + target_percentage)
            
        if not short_position and not long_position and intial_amount > 0 and previous_ema_large_1 >= previous_ema_small_1 and ema_large < ema_small:
            
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
        
            
        if not long_position and not short_position  and intial_amount > 0 and previous_ema_large_1 <= previous_ema_small_1 and ema_large > ema_small:
            
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
            
        previous_ema_small_2 = previous_ema_small_1
        previous_ema_small_1 = ema_small
        previous_ema_large_2 = previous_ema_large_1
        previous_ema_large_1 = ema_large
        
     
    data_file = open(f'./EMA_Backtest/Backtest_Results/Intraday/{stock_name}_Intraday_Backtest_Results_EMA.csv', 'w', newline='')       
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
