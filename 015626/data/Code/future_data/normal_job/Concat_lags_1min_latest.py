# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 23:22:43 2020

@author: appadmin
"""
from multifactor.IO import IO
import multifactor.utility.dt as udt
from multifactor.data.utils import *
import os


Contract_Name_IC = 'IC'
Contract_Name_IF = 'IF'
Contract_Name_IH = 'IH'
# Time Lag
tt = 0
#holding period in seconds
freq = 60
# Location of tick data in seperate csvs
# NO '/' AT THE END !
read_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/MAIN/'
read_path_IC = read_root_path + 'IC_CFE'
read_path_IF = read_root_path + 'IF_CFE'
read_path_IH = read_root_path + 'IH_CFE'
# Save Path
# NO '/' AT THE END !
save_root_path = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_FUTURES/tick_to_minute/'
save_path_IC = save_root_path + 'IC'
save_path_IF = save_root_path + 'IF'
save_path_IH = save_root_path + 'IH'
h5rootpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/TICK_TO_MINUTE/MD_SIF_TICK_TO_MINUTE_MAIN.h5'

df_allcontract = IO.read_data([20200101, 21000101], alt = h5rootpath)
sdate, _, cdate_list = check_update_date(int(str(df_allcontract.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
begin_date = cdate_list[1]
end_date = cdate_list[-1]

begin_date = str(begin_date)
end_date = str(end_date)

for p in [save_path_IC,save_path_IF,save_path_IH]:
    if not os.path.exists(p):
        os.makedirs(p)
        
def file_flag_check(date):
    path = os.path.join(read_path_IC, date +'.csv')
    return os.path.exists(path)

print('------wait minute flag')
while True:
    if file_flag_check(end_date):
        break
print('flag no problem, start generate data')
# Don't change anything below this line
######################################################################################################################################
factor_number = 20
li = ['dt','tradingdate', 'open', 'close', 'high', 'low', 'value','volume', 'vwap', 'twap', 'position', 'ticktime']
li_factors = ['dt','OrderFlowImbalanceLv1','OrderFlowImbalanceRatioLv1', 'PriceMean', 'PriceVol', 'PriceSkew', 'PriceKurt', 'RetMean', 'RetVol', 'RetSkew', 'RetKurt', 'AbsDistance', 'VolumeMean', 'VolumeStd', 'HighVolumeCount', 'BidAskMean', 'BidAskVol', 'BASWeighted', 'BASSign', 'BASCorrV', 'TickCounts']

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
def calc(columns,data_dict, data_dict_minute, data_dict_minute_concat, data_dict_factor_concat, factor_number, count, count1, count2, temp, bl, b, contract_3, n = freq):
    dt = columns.index('dt')
    last_px = columns.index('LastPx')
    total_amount = columns.index('TotalValueTrade')
    total_volume = columns.index('TotalVolumeTrade')
    bas = columns.index('BidAskSpread')
    basw = columns.index('BidAskSpreadWeighted')
    #amount = columns.index('Amount')
    volume = columns.index('Volume')
    date = columns.index('TradingDate')
    position = columns.index('OpenInterest')
    s1p = columns.index('Sell1Price')
    s1q = columns.index('Sell1OrderQty')
    b1p = columns.index('Buy1Price')
    b1q = columns.index('Buy1OrderQty')

    try:
            if ((float(b[s1p]) == 0 and float(b[s1q])==0) or (float(b[b1p]) == 0 and float(b[b1q]) == 0)) and ((('2015' in b[dt]) and ((' 09:14' not in b[dt]) and (' 09:15:0' not in b[dt]))) or (('2015' not in b[dt]) and ((' 09:29' not in b[dt]) and (' 09:30:0' not in b[dt])))):
                
                data_dict[count]=[np.nan]*len(b)
                
                data_dict[count][dt] = b[dt]
                data_dict[count][date] = b[date]
            else:
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
                        data_dict_minute_concat[count1+1] = [0.0]*12
                        data_dict_factor_concat[count1+1] = [0.0]*(1+factor_number)
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
                            data_dict_factor_concat[count1-1][0] = data_dict_minute[count1-1][0][dt]
                            #Trading date
                            data_dict_minute_concat[count1-1][1] = data_dict_minute[count1-1][0][date]
                            

                            #maximum = list(map(max, *data_dict_minute[count1-1]))
                            #minimum = list(map(min, *data_dict_minute[count1-1]))
                            
                            # Market Microstructure                            
                            List_o = np.array(data_dict_minute[count1-1])
                            if (('2015' in data_dict_minute[count1-1][0][dt]) and (' 09:15' in data_dict_minute[count1-1][0][dt]) and (' 09:14' in data_dict_minute[count1-2][0][dt])) or \
                                (('2015' not in data_dict_minute[count1-1][0][dt]) and (' 09:30' in data_dict_minute[count1-1][0][dt]) and (' 09:29' in data_dict_minute[count1-2][0][dt])):

                                List_o = np.concatenate((np.array(data_dict_minute[count1-2]), np.array(data_dict_minute[count1-1])), axis = 0)
                                
                            List3 = List_o[:, -3].astype(float)
                            List4 = List_o[:, -2].astype(float)
                            List3_mean = np.nanmean(List3)
                            List4_mean = np.nanmean(List4)
                            List_prce = List_o[:, last_px].astype(float)
                            List_prce_mean = np.nanmean(List_prce)
                            
                            List_volume = List_o[:, volume].astype(float)
                            volume_mean = np.nanmean(List_volume)
                            List_bas = List_o[:, bas].astype(float)
                            List_basw = List_o[:, basw].astype(float)
                            bas_mean = np.nanmean(List_bas)
                            basw_mean = np.nanmean(List_basw)
                            List_twap = np.nanmean(List_prce)
                            data_dict_factor_concat[count1-1][1] = List3_mean
                            data_dict_factor_concat[count1-1][2] = List4_mean
                            data_dict_factor_concat[count1-1][3] = List_prce_mean
                            data_dict_factor_concat[count1-1][12] = volume_mean
                            data_dict_factor_concat[count1-1][15] = bas_mean
                            data_dict_factor_concat[count1-1][17] = basw_mean
                            data_dict_factor_concat[count1-1][20] = len(data_dict_minute[count1-1])
                            if len(data_dict_minute[count1-1])>1:
                                
                                List_prce_diff = np.diff(List_prce)/List_prce[:-1]
                                sign = [0] + list(np.where(List_prce_diff>0, 1, np.where(List_prce_diff==0, 0 , -1)))                                                    
                                List_mean_diff = np.nanmean(List_prce_diff)
                                List_vol = np.std(List_prce)
                                List_vol_diff = np.std(List_prce_diff)
                                List_ad = np.sum(np.abs(List_prce_diff))
                                List_skew = pd.Series(List_prce).skew()
                                List_skew_diff = pd.Series(List_prce_diff).skew()
                                List_kurt = pd.Series(List_prce).kurt()
                                List_kurt_diff = pd.Series(List_prce_diff).kurt()
                                List_prce_diff = np.diff(List_prce)/List_prce[:-1]
                                sign = [0] + list(np.where(List_prce_diff>0, 1, np.where(List_prce_diff==0, 0 , -1)))
                                volume_std = np.std(List_volume)
                                high_list = List_volume[List_volume > volume_mean * 1.2]
                                volume_count = len(high_list)
                                bas_std = np.std(List_bas)
                                corr_v = np.corrcoef(List_bas, List_volume)[0, 1]
                                data_dict_factor_concat[count1-1][4] = List_vol
                                data_dict_factor_concat[count1-1][5] = List_skew
                                data_dict_factor_concat[count1-1][6] = List_kurt
                                data_dict_factor_concat[count1-1][7] = List_mean_diff 
                                data_dict_factor_concat[count1-1][8] = List_vol_diff
                                data_dict_factor_concat[count1-1][9] = List_skew_diff
                                data_dict_factor_concat[count1-1][10] = List_kurt_diff
                                data_dict_factor_concat[count1-1][11] = List_ad
                                data_dict_factor_concat[count1-1][13] = volume_std
                                data_dict_factor_concat[count1-1][14] = volume_count
                                data_dict_factor_concat[count1-1][16] = bas_std
                                data_dict_factor_concat[count1-1][18] = np.nanmean(List_bas*sign)
                                data_dict_factor_concat[count1-1][19] = corr_v
                            else:
                                data_dict_factor_concat[count1-1][4] = np.nan
                                data_dict_factor_concat[count1-1][5] = np.nan
                                data_dict_factor_concat[count1-1][6] = np.nan
                                data_dict_factor_concat[count1-1][7] = np.nan 
                                data_dict_factor_concat[count1-1][8] = np.nan
                                data_dict_factor_concat[count1-1][9] = np.nan
                                data_dict_factor_concat[count1-1][10] = np.nan
                                data_dict_factor_concat[count1-1][11] = np.nan
                                data_dict_factor_concat[count1-1][13] = np.nan
                                data_dict_factor_concat[count1-1][14] = np.nan
                                data_dict_factor_concat[count1-1][16] = np.nan
                                data_dict_factor_concat[count1-1][18] = np.nan
                                data_dict_factor_concat[count1-1][19] = np.nan
                            
            


                            
                            #Open
                            data_dict_minute_concat[count1-1][2] = data_dict_minute[count1-1][0][last_px]
                            #Close
                            data_dict_minute_concat[count1-1][3] = data_dict_minute[count1-1][-1][last_px]
                            
                            
                            #High
                            data_dict_minute_concat[count1-1][4] = np.nanmax(List_o[:, last_px].astype(float))
                            #Low
                            data_dict_minute_concat[count1-1][5] = np.nanmin(List_o[:, last_px].astype(float))

                            #twap
                            data_dict_minute_concat[count1-1][9] = List_twap
                            
                            
                        else:
                            pass
                        
                        #Amount&volume
                        if count1-2>=0:
                            if (('2015' in data_dict_minute[count1-1][0][dt]) and (' 09:15' in data_dict_minute[count1-1][0][dt]) and (' 09:14' in data_dict_minute[count1-2][0][dt])) or \
                                (('2015' not in data_dict_minute[count1-1][0][dt]) and (' 09:30' in data_dict_minute[count1-1][0][dt]) and (' 09:29' in data_dict_minute[count1-2][0][dt])):
                                data_dict_minute_concat[count1-1][6] = float(data_dict_minute[count1-1][-1][total_amount])
                                data_dict_minute_concat[count1-1][7] = float(data_dict_minute[count1-1][-1][total_volume])
                            else:
                                data_dict_minute_concat[count1-1][6] = float(data_dict_minute[count1-1][-1][total_amount])-float(data_dict_minute[count1-2][-1][total_amount])
                                data_dict_minute_concat[count1-1][7] = float(data_dict_minute[count1-1][-1][total_volume])-float(data_dict_minute[count1-2][-1][total_volume])
                        
                        else:
                            pass
                        
                        
                        #Vwap
                        if data_dict_minute_concat[count1-1][7]!= 0:
                            if contract_3 == 'IC':
                                data_dict_minute_concat[count1-1][8] = 0.01*data_dict_minute_concat[count1-1][6]/data_dict_minute_concat[count1-1][7]/2
                            else:
                                data_dict_minute_concat[count1-1][8] = 0.01*data_dict_minute_concat[count1-1][6]/data_dict_minute_concat[count1-1][7]/3
                        else:
                            try:
                                data_dict_minute_concat[count1-1][8] =  data_dict_minute_concat[count1-2][8]
                            except:
                                data_dict_minute_concat[count1-1][8] = np.nan
                        

                        
                        #Position
                        data_dict_minute_concat[count1-1][10] = data_dict_minute[count1-1][-1][position]
                
                        #Tick Time
                        data_dict_minute_concat[count1-1][11] = data_dict_minute[count1-1][-1][dt]
                        
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
                
                    if data_dict_factor_concat[count1-1][8] == 0 and data_dict_factor_concat[count1-1][9] == 0:
                    
                        data_dict_factor_concat[count1-1][1:] = [np.nan]*len(data_dict_factor_concat[count1-1][1:])
                #pass
            
            count = count + 1
            
    except: 
        data_dict_minute[count1] = [i for i in data_dict_minute[count1] if i != 0]

    return data_dict, data_dict_minute, data_dict_minute_concat, data_dict_factor_concat, count, count1, count2, temp, bl, b

# Create a dataframe from dictionary
def create_dict(w1,Contract, factor_number, l = li, l_factor = li_factors, n = freq):
    columns_0 = list(w1.columns)

    count = 0
    count1 = 0
    count2 = 0
    temp = [] 
    bl = 0 
    data_dict_0 = {}
    data_dict_minute_0 = {}
    data_dict_minute_concat_0 = {}
    data_dict_factor_concat = {}

    for index, row in w1.iterrows():

        temp_row = list(row)
        
        data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, data_dict_factor_concat, count, count1, count2, temp, bl, temp_row = calc(columns_0, data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, data_dict_factor_concat,factor_number, count, count1, count2, temp, bl, temp_row, Contract)


        
    data_dict_minute_0[len(data_dict_minute_0)-1] =  [i for i in data_dict_minute_0[len(data_dict_minute_0)-1] if i != 0]

    
    df_0 = pd.DataFrame(data_dict_minute_concat_0).T


    df_0.columns = l
    if df_0['dt'].iloc[0] == 0:
        df_0 = df_0.iloc[1:]

    df_0 = df_0[(df_0.T != 0).any()]    
    df_0 = df_0.reset_index(drop = True)
    

    
    df_1 = pd.DataFrame( data_dict_factor_concat).T
    df_1.columns = l_factor
    if df_1['dt'].iloc[0] == 0:
        df_1 = df_1.iloc[1:]    
    
    df_1 = df_1[(df_1.T != 0).any()]
    df_1 = df_1.reset_index(drop = True)
    
    df_0['dt'] = [(item[:17]+str(int(item[17:19])-int(item[17:19])%freq)) for item in df_0['dt']]
    df_1['dt'] = [(item[:17]+str(int(item[17:19])-int(item[17:19])%freq)) for item in df_1['dt']]
    
    df_0['dt'] = [(item[:17]+'0'+item[-1]) if len(item) < 19 else item for item in df_0['dt']] 
    df_1['dt'] = [(item[:17]+'0'+item[-1]) if len(item) < 19 else item for item in df_1['dt']]
    return df_0, df_1, data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, data_dict_factor_concat


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

def print_csv(Contract_3, Contract_t, read_path, save_path, tt = tt, factor_number = factor_number, freq = freq):
    df_s = pd.DataFrame()
    for item in Contract_t:
    

        now = item

        if now in Contract_t:
            start = time.time()

            filename_2 = read_path + '/'+now
            
            w3 = pd.read_csv(filename_2)
            w3_30 = w3.copy()
            now_temp = str(now)[0:4] + '-' + str(now)[4:6] + '-' + str(now)[6:8]

            if int(now[:4]) >= 2016:
                base = pd.Timestamp('%s 09:30:00.000'%now_temp)
                numdays = 20000
                date_list = [base + datetime.timedelta(seconds=x*freq) for x in range(numdays)]
                date_list1 = [item for item in date_list if (item < pd.Timestamp('%s 15:00:00.000'%now_temp)) & (~((item >= pd.Timestamp('%s 11:30:00.000'%now_temp)) & (item < pd.Timestamp('%s 13:00:00.000'%now_temp))))]
            else:
                base = pd.Timestamp('%s 09:15:00.000'%now_temp)
                numdays = 20000
                date_list = [base + datetime.timedelta(seconds=x*freq) for x in range(numdays)]
                date_list1 = [item for item in date_list if (item < pd.Timestamp('%s 15:15:00.000'%now_temp)) & (~((item >= pd.Timestamp('%s 11:30:00.000'%now_temp)) & (item < pd.Timestamp('%s 13:00:00.000'%now_temp))))]
                
                
            pd_date = pd.DataFrame()
            pd_date['tempdt'] = date_list1
            pd_date = pd_date.set_index('tempdt')
            # time lags
            dt_list = pd.to_datetime(w3_30['dt'], format='%Y-%m-%d %H:%M:%S.%f')
            dt_list = dt_list - datetime.timedelta(seconds=tt)
            dt_list = dt_list.astype(str)
            w3_30['dt'] = dt_list
           
            for w in [w3_30]:   
                w['Volume'] = w['TotalVolumeTrade'].diff()
                w['Amount'] = w['TotalValueTrade'].diff()
                w['BidAskSpread'] = w['Sell1Price'] - w['Buy1Price']
                w['BidAskSpreadWeighted'] = w['BidAskSpread']*(w['Sell1OrderQty']+w['Buy1OrderQty'])
                w['OrderFlowImbalanceLv1'] = w['Buy1OrderQty'] - w['Sell1OrderQty']
                w['OrderFlowImbalanceRatioLv1'] = (w['Buy1OrderQty'] - w['Sell1OrderQty'])/(w['Buy1OrderQty'] + w['Sell1OrderQty'])


            w3['Name']= Contract_3
            w3_30['Name'] = Contract_3
            df_0, df, data_dict_0_2, data_dict_minute_0_2, data_dict_minute_concat_0_2, data_dict_factor_concat_0_2 = create_dict(w3_30, Contract_3, factor_number)
            
            minute_temp = 0
            if int(now[:4])<2016:
                minute_temp = 14
            else:
                minute_temp = 29
            # Changing back the time
            if tt != 0:              
                dt_list2 = pd.to_datetime(df_0['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                dt_list2 = dt_list2 + datetime.timedelta(seconds=tt)
                if dt_list2.iloc[0].minute == minute_temp:
                    dt_list2.iloc[0] = dt_list2.iloc[0] + datetime.timedelta(seconds=(60-tt))
                df_0['dt'] = dt_list2
                df_0 = df_0.set_index('dt')
            
                dt_list3 = pd.to_datetime(df_0['ticktime'], format='%Y-%m-%d %H:%M:%S.%f')
                dt_list3 = dt_list3 + datetime.timedelta(seconds=tt)
                if dt_list3.iloc[0].minute == minute_temp:
                    dt_list3.iloc[0] = dt_list3.iloc[0] + datetime.timedelta(seconds=(60-tt))
                df_0['ticktime'] = dt_list3
                    
                dt_list4 = pd.to_datetime(df['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                dt_list4 = dt_list4 + datetime.timedelta(seconds=tt)
                if dt_list4.iloc[0].minute == minute_temp:
                    dt_list4.iloc[0] = dt_list4.iloc[0] + datetime.timedelta(seconds=(60-tt))
                df['dt'] = dt_list4
                df = df.set_index('dt')
            else:
                df_0['dt'] = pd.to_datetime(df_0['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                df_0 = df_0.set_index('dt')
                df['dt'] = pd.to_datetime(df['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                df = df.set_index('dt')

            df_st = pd.concat([df_0, df], axis = 1)
            df_s = pd.concat([df_st, pd_date], axis = 1)
            

            if int(now[:4]) >= 2016:
                df_s = select_dates(df_s)
                df_s = df_s.where(~df_s.isnull().all(axis=1), df_s.fillna(method='ffill'))
                w3.index = pd.to_datetime(w3['dt'], format='%Y-%m-%d %H:%M:%S.%f')

            else:
                df_s = select_dates1(df_s)
                df_s = df_s.where(~df_s.isnull().all(axis=1), df_s.fillna(method='ffill'))
                w3.index = pd.to_datetime(w3['dt'], format='%Y-%m-%d %H:%M:%S.%f')
                
                
            df_s.to_csv(save_path +'/' + now)
            print(time.time()-start)
            print(now)
            


contract_IC = get_list(read_path_IC)
print_csv(Contract_Name_IC, contract_IC, read_path_IC, save_path_IC)
contract_IH = get_list(read_path_IH)
print_csv(Contract_Name_IH, contract_IH, read_path_IH, save_path_IH)
contract_IF = get_list(read_path_IF)
print_csv(Contract_Name_IF, contract_IF, read_path_IF, save_path_IF)

# 以下为更新csv数据为h5
def get_df(path, ticker):
    mdf = pd.DataFrame()
    for c in cdate_list:
        print(ticker, c)
        csv_path = os.path.join(path, str(c) + '.csv')
        if os.path.exists(csv_path):
            a = pd.read_csv(csv_path)
        else:
            continue
        a = a.rename(columns = {a.columns.tolist()[0]:'dt','value':'amount'})
        a = a.drop(['tradingdate','ticktime'], axis = 1)
        a['dt'] = pd.to_datetime(a['dt'])
        a['Ticker'] = ticker
        a['HighVolumeCount'] = a['HighVolumeCount'].astype('float')
        a['TickCounts'] = a['TickCounts'].astype('float')
        mdf = mdf.append(a)
    mdf = mdf.set_index('dt').sort_index()
    
    t_days_list = udt.get_trading_date_range(str(mdf.index[0].date()).replace('-',''),str(mdf.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:57:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    mdf = index_df.join(mdf, how = 'left')
    for col in ['open','high','low','close','position']:
        mdf[col] = mdf[col].fillna(method = 'ffill')
    for col in ['volume','amount']:
        mdf[col] = mdf[col].fillna(value = 0)
                        
    return mdf.reset_index().set_index(['dt','Ticker'])
 
print('start generate h5')
icdf = get_df(save_path_IC, 'IC.CFE')
ifdf = get_df(save_path_IF, 'IF.CFE')
ihdf = get_df(save_path_IH, 'IH.CFE')

alldf = icdf.append(ifdf).append(ihdf)
alldf = alldf.sort_index()
alldf['share'] = alldf.amount / alldf.vwap
IO.pd_hdf5_writer(alldf, h5rootpath, dataset = 'tick_to_minute',append=True)

