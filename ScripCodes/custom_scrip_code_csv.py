import csv
import json
import time

t1 = time.time()

scrip_code_file = open('./ScripCodes/scripmaster-csv-format.csv')
scrip_code_data = csv.DictReader(scrip_code_file)

new_scrip_code_data = []
new_scrip_code_dict = {}    

# print(scrip_code_data.fieldnames)

for row in scrip_code_data:
    
    if row['Exch'] == 'N' and row['ExchType'] == 'C' and row['Series'] == 'EQ':
        
        new_scrip_code_data.append(row)
        new_scrip_code_dict[row['Name']] = row
    

json_data_file = open('./ScripCodes/new-scripcode-json.json', 'w', newline='')       
json.dump(new_scrip_code_dict, json_data_file)


data_file = open('./ScripCodes/new-scripcode-file.csv', 'w', newline='')       
data_list = csv.DictWriter(data_file, fieldnames = [
    'Exch', 
    'ExchType', 
    'Scripcode', 
    'Name', 
    'Series', 
    'Expiry', 
    'CpType', 
    'StrikeRate', 
    'WireCat', 
    'ISIN', 
    'FullName'
])

data_list.writeheader()
data_list.writerows(new_scrip_code_data)

t2 = time.time()
print('Your Code took', t2 - t1, 's to execute')