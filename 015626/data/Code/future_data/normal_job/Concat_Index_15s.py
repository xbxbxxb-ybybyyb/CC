# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 17:01:10 2021

@author: appadmin
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 23:22:43 2020

@author: appadmin
"""

Contract_Name_IC = 'ZZ500'
Contract_Name_IF = 'HS300'
Contract_Name_IH = 'SH50'
# Time Lag
tt = 0
#holding period in seconds
freq = 15
# Location of tick data in seperate csvs
# NO '/' AT THE END !
read_path_IC = '/data/user/015626/data/share/MD/CHINA_INDEX/5s/ZZ500'
read_path_IF = '/data/user/015626/data/share/MD/CHINA_INDEX/5s/HS300'
read_path_IH = '/data/user/015626/data/share/MD/CHINA_INDEX/5s/SH50'
# Save Path
# NO '/' AT THE END !
save_path_IC = '/data/user/015626/data/share/LOCAL_DATA/CSV/tick_to_15s/CHINA_INDEX/ZZ500'
save_path_IF = '/data/user/015626/data/share/LOCAL_DATA/CSV/tick_to_15s/CHINA_INDEX/HS300'
save_path_IH = '/data/user/015626/data/share/LOCAL_DATA/CSV/tick_to_15s/CHINA_INDEX/SH50'

begin_date = '20140101'
end_date = '20210118'

# Don't change anything below this line
######################################################################################################################################
factor_number = 20
li = ['dt','open', 'close', 'high', 'low', 'value','volume', 'ticktime']

import pandas as pd
import numpy as np
import time
from os import listdir
from os.path import isfile, join
import datetime
import warnings

warnings.filterwarnings('ignore')

def get_list(read_path):
    contract_3 = [f for f in listdir(read_path+'/') if isfile(join(read_path, f))]
    list_temp = [int(item[:8]) for item in contract_3]
    list_temp = [str(item) for item in list_temp if item >= int(begin_date) and item <= int(end_date)]
    Contract_t_3 = [item + '.csv' for item in list_temp]
    return Contract_t_3

# Calculate relevant results and put them into dictionaries
def calc(columns,data_dict, data_dict_minute, data_dict_minute_concat, count, count1, count2, temp, bl, b, contract_3, n = freq):
    dt = columns.index('dt')
    last_px = columns.index('LastPx')
    total_amount = columns.index('TotalValueTrade')
    total_volume = columns.index('TotalVolumeTrade')


    try:

            data_dict[count]=b
                

            try:
                if count>0:
                    if count == 1:
                        temp = data_dict[count].copy()

                    else:
                        pass
                    
                    if (int(data_dict[count][dt][11:13])*3600 + int(data_dict[count][dt][14:16])*60 + int(data_dict[count][dt][17:19]) - (int(temp[dt][11:13])*3600+int(temp[dt][14:16])*60 + int(temp[dt][17:19]) - int(temp[dt][17:19])%n) >= n) or (int(data_dict[count][dt][17:19])%n == 0 and data_dict[count][dt][17:19] != temp[dt][17:19]):
                        #print(seconds_temp)

                        bl = 1
                        temp = data_dict[count]
 

                    else:
                        bl = 0

                    if bl ==1 or count == 1:
                                                                   
                        data_dict_minute[count1+1] = [0.0]*10000
                        data_dict_minute[count1+1][0] = data_dict[count]
                        data_dict_minute_concat[count1+1] = [0.0]*8

                        count1 = count1 + 1
                        if count1 == 1:
                            if data_dict_minute[count1][1][dt][11:16] == data_dict[count1-1][0][dt][11:16]:
                                data_dict_minute[count1][0] = data_dict[count1-1] + data_dict_minute[count1][0]
                            else:
                                pass
                        else:
                            pass
                    
                        data_dict_minute[count1-1] = [i for i in data_dict_minute[count1-1] if i != 0]
                        
                        if count1 >= 2:
                            # Date-Time
                            data_dict_minute_concat[count1-1][0] = data_dict_minute[count1-1][0][dt]

                            

                            #maximum = list(map(max, *data_dict_minute[count1-1]))
                            #minimum = list(map(min, *data_dict_minute[count1-1]))
                            
                            # Market Microstructure                            
                            List_o = np.array(data_dict_minute[count1-1])
                            

                            
            


                            
                            #Open
                            data_dict_minute_concat[count1-1][1] = data_dict_minute[count1-1][0][last_px]
                            #Close
                            data_dict_minute_concat[count1-1][2] = data_dict_minute[count1-1][-1][last_px]
                            
                            
                            #High
                            data_dict_minute_concat[count1-1][3] = np.nanmax(List_o[:, last_px].astype(float))
                            #Low
                            data_dict_minute_concat[count1-1][4] = np.nanmin(List_o[:, last_px].astype(float))


                            
                            
                        else:
                            pass
                        
                        #Amount&volume
                        if count1-2>=0:
                            
                            data_dict_minute_concat[count1-1][5] = float(data_dict_minute[count1-1][-1][total_amount])-float(data_dict_minute[count1-2][-1][total_amount])
                            data_dict_minute_concat[count1-1][6] = float(data_dict_minute[count1-1][-1][total_volume])-float(data_dict_minute[count1-2][-1][total_volume])
                    
                        else:
                            pass
                        
  

                        #Tick Time
                        data_dict_minute_concat[count1-1][7] = data_dict_minute[count1-1][-1][dt]
                        
                        count2 = 0
                        
                    else:
                        data_dict_minute[count1][count2+1] = data_dict[count]
                        count2 = count2 + 1
                else:
                    data_dict_minute[count1] = [data_dict[count]]
                    #data_dict_minute_concat[count1] = [0.0]*10
                    
            except:
                if count1>=2:
                    if data_dict_minute_concat[count1-1][2] == 0 and data_dict_minute_concat[count1-1][6] == 0:
                    
                        data_dict_minute_concat[count1-1][2:-1] = [np.nan]*len(data_dict_minute_concat[count1-1][2:-1])
                
                #pass
            
            count = count + 1
            
    except: 
        data_dict_minute[count1] = [i for i in data_dict_minute[count1] if i != 0]

    return data_dict, data_dict_minute, data_dict_minute_concat,  count, count1, count2, temp, bl, b

# Create a dataframe from dictionary
def create_dict(w1,Contract, l = li, n = freq):
    columns_0 = list(w1.columns)

    count = 0
    count1 = 0
    count2 = 0
    temp = [] 
    bl = 0 
    data_dict_0 = {}
    data_dict_minute_0 = {}
    data_dict_minute_concat_0 = {}


    for index, row in w1.iterrows():

        temp_row = list(row)
        
        data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, count, count1, count2, temp, bl, temp_row = calc(columns_0, data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, count, count1, count2, temp, bl, temp_row, Contract)


        
    data_dict_minute_0[len(data_dict_minute_0)-1] =  [i for i in data_dict_minute_0[len(data_dict_minute_0)-1] if i != 0]

    
    df_0 = pd.DataFrame(data_dict_minute_concat_0).T


    df_0.columns = l
    if df_0['dt'].iloc[0] == 0:
        df_0 = df_0.iloc[1:]

    df_0 = df_0[(df_0.T != 0).any()]    
    df_0 = df_0.reset_index(drop = True)
    

    


    
    df_0['dt'] = [(item[:17]+str(int(item[17:19])-int(item[17:19])%freq)) for item in df_0['dt']]

    
    df_0['dt'] = [(item[:17]+'0'+item[-1]) if len(item) < 19 else item for item in df_0['dt']] 

    return df_0, data_dict_0, data_dict_minute_0, data_dict_minute_concat_0


def select_dates(df):
    idx = df.index
    t = idx[((idx.hour == 9) & (idx.minute >= 30)) | (idx.hour == 10) | ((idx.hour ==11) & (idx.minute < 30))| (idx.hour == 13) | ((idx.hour == 14) & (idx.minute <= 59))]
    t = list(t.sort_values())
    return df.loc[t]    

def select_dates1(df):
    idx = df.index
    t = idx[((idx.hour == 9) & (idx.minute >= 15)) | (idx.hour == 10) | ((idx.hour ==11) & (idx.minute < 30))| (idx.hour == 13) | ((idx.hour == 14) & (idx.minute <= 59)) |((idx.hour == 15) & (idx.minute < 15))]
    t = list(t.sort_values())
    return df.loc[t] 

def print_csv(Contract_3, Contract_t, read_path, save_path, tt = tt):

    for item in Contract_t:
    

        now = item
        

        if now in Contract_t:
            start = time.time()

            filename_2 = read_path + '/'+now

            w3 = pd.read_csv(filename_2)
            w3_30 = w3.copy()
            
            # time lags
            dt_list = pd.to_datetime(w3_30['dt'], format='%Y-%m-%d %H:%M:%S.%f')
            dt_list = dt_list - datetime.timedelta(seconds=tt)
            dt_list = dt_list.astype(str)
            w3_30['dt'] = dt_list
           

            w3['Name']= Contract_3
            w3_30['Name'] = Contract_3
            df_0, data_dict_0_2, data_dict_minute_0_2, data_dict_minute_concat_0_2 = create_dict(w3_30, Contract_3)
             
            # Changing back the time
            if tt != 0:              
                dt_list2 = pd.to_datetime(df_0['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                dt_list2 = dt_list2 + datetime.timedelta(seconds=tt)
                if dt_list2.iloc[0].minute == 29:
                    dt_list2.iloc[0] = dt_list2.iloc[0] + datetime.timedelta(seconds=(60-tt))
                df_0['dt'] = dt_list2
                df_0 = df_0.set_index('dt')
            
                dt_list3 = pd.to_datetime(df_0['ticktime'], format='%Y-%m-%d %H:%M:%S.%f')
                dt_list3 = dt_list3 + datetime.timedelta(seconds=tt)
                if dt_list3.iloc[0].minute == 29:
                    dt_list3.iloc[0] = dt_list3.iloc[0] + datetime.timedelta(seconds=(60-tt))
                df_0['ticktime'] = dt_list3
            

            else:
                df_0['dt'] = pd.to_datetime(df_0['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                df_0 = df_0.set_index('dt')

            
            df_0 = select_dates(df_0)
            df_0.to_csv(save_path +'/' + now)
            print(time.time()-start)
            print(item)
            

contract_IC = get_list(read_path_IC)
print_csv(Contract_Name_IC, contract_IC, read_path_IC, save_path_IC)
contract_IH = get_list(read_path_IH)
print_csv(Contract_Name_IH, contract_IH, read_path_IH, save_path_IH)
contract_IF = get_list(read_path_IF)
print_csv(Contract_Name_IF, contract_IF, read_path_IF, save_path_IF)

