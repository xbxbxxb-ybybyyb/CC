Contract_3 = 'IF'
# Time Lag
tt = 0
# Location of tick data, A LOT OF csvs
read_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/MAIN/' + Contract_3 + '_CFE/'
# Save Path
save_path = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/tick_to_minute_' + str(tt) + '_' + str(tt) + '/' + Contract_3 + '/'
begin_date = '20120930'
end_date = '20200930'

###############################################################################################################################
import pandas as pd
import numpy as np
import time
import os
from os import listdir
from os.path import isfile, join
import datetime
from multiprocessing.pool import Pool

if not os.path.exists(save_path):
    os.makedirs(save_path)


contract_3 = [f for f in listdir(read_path+'/') if isfile(join(read_path, f))]
list_temp = [int(item[:8]) for item in contract_3]
list_temp = [str(item) for item in list_temp if item >= int(begin_date) and item <= int(end_date)]
Contract_t_3 = [item + '.csv' for item in list_temp]
li = ['dt','tradingdate', 'open', 'close', 'high', 'low', 'value','volume', 'vwap', 'twap', 'position', 'ticktime']
li_factors = ['dt','OrderFlowImbalanceLv1','OrderFlowImbalanceRatioLv1', 'PriceMean', 'PriceVol', 'PriceSkew', 'PriceKurt', 'RetMean', 'RetVol', 'RetSkew', 'RetKurt', 'AbsDistance', 'VolumeMean', 'VolumeStd', 'HighVolumeCount', 'BidAskMean', 'BidAskVol', 'BASWeighted', 'BASSign', 'BASCorrV']

# Calculate relevant results and put them into dictionaries
def calc(n, columns,data_dict, data_dict_minute, data_dict_minute_concat, data_dict_factor_concat, factor_number, count, count1, count2, temp, bl, b):
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
            if (float(b[s1p]) == 0 and float(b[s1q])==0) or (float(b[b1p]) == 0 and float(b[b1q]) == 0):
                
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
                
                    if int(data_dict[count][dt][11:13])*60 + int(data_dict[count][dt][14:16]) - (int(temp[dt][11:13])*60+int(temp[dt][14:16])) >= n:
                        bl = 1
                        temp = data_dict[count]
                    else:
                        bl = 0
                                                
               
                    if bl ==1 or count == 1:                                              
                        data_dict_minute[count1+1] = [0.0]*5000
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
                            data_dict_minute_concat[count1-1][0] = data_dict_minute[count1-1][0][dt][:17]+'00'
                            data_dict_factor_concat[count1-1][0] = data_dict_minute[count1-1][0][dt][:17]+'00'
                            #Trading date
                            data_dict_minute_concat[count1-1][1] = data_dict_minute[count1-1][0][date]
                            #Tick Time
                            data_dict_minute_concat[count1-1][10] = data_dict_minute[count1-1][-1][dt]

                            maximum = list(map(max, *data_dict_minute[count1-1]))
                            minimum = list(map(min, *data_dict_minute[count1-1]))
                            
                            # Market Microstructure
                            List_o = np.array(data_dict_minute[count1-1])
                            List3 = List_o[:, -3].astype(float)
                            List4 = List_o[:, -2].astype(float)
                            List3_mean = np.mean(List3)
                            List4_mean = np.mean(List4)
                            List_prce = List_o[:, last_px].astype(float)
                            List_prce_diff = np.diff(List_prce)/List_prce[:-1]
                            sign = [0] + list(np.where(List_prce_diff>0, 1, np.where(List_prce_diff==0, 0 , -1)))
                            
                            List_prce_mean = np.mean(List_prce)
                            List_mean_diff = np.mean(List_prce_diff)
                            List_vol = np.std(List_prce)
                            List_vol_diff = np.std(List_prce_diff)
                            List_ad = np.sum(np.abs(List_prce_diff))
                            List_skew = pd.Series(List_prce).skew()
                            List_skew_diff = pd.Series(List_prce_diff).skew()
                            List_kurt = pd.Series(List_prce).kurt()
                            List_kurt_diff = pd.Series(List_prce_diff).kurt()
                            List_volume = List_o[:, volume].astype(float)
                            volume_mean = np.mean(List_volume)
                            volume_std = np.std(List_volume)
                            high_list = List_volume[List_volume > volume_mean * 1.2]
                            volume_count = len(high_list)
                            List_bas = List_o[:, bas].astype(float)
                            List_basw = List_o[:, basw].astype(float)
                            bas_mean = np.mean(List_bas)
                            bas_std = np.std(List_bas)
                            basw_mean = np.mean(List_basw)
                            corr_v = np.corrcoef(List_bas, List_volume)[0, 1]
                            
                            List_twap = np.mean(List_prce)
                            data_dict_factor_concat[count1-1][1] = List3_mean
                            data_dict_factor_concat[count1-1][2] = List4_mean
                            data_dict_factor_concat[count1-1][3] = List_prce_mean
                            data_dict_factor_concat[count1-1][4] = List_vol
                            data_dict_factor_concat[count1-1][5] = List_skew
                            data_dict_factor_concat[count1-1][6] = List_kurt
                            data_dict_factor_concat[count1-1][7] = List_mean_diff 
                            data_dict_factor_concat[count1-1][8] = List_vol_diff
                            data_dict_factor_concat[count1-1][9] = List_skew_diff
                            data_dict_factor_concat[count1-1][10] = List_kurt_diff
                            data_dict_factor_concat[count1-1][11] = List_ad
                            data_dict_factor_concat[count1-1][12] = volume_mean
                            data_dict_factor_concat[count1-1][13] = volume_std
                            data_dict_factor_concat[count1-1][14] = volume_count
                            data_dict_factor_concat[count1-1][15] = bas_mean
                            data_dict_factor_concat[count1-1][16] = bas_std
                            data_dict_factor_concat[count1-1][17] = basw_mean
                            data_dict_factor_concat[count1-1][18] = np.mean(List_bas*sign)
                            data_dict_factor_concat[count1-1][19] = corr_v
                            
                            #Open
                            data_dict_minute_concat[count1-1][2] = data_dict_minute[count1-1][0][last_px]
                            #Close
                            data_dict_minute_concat[count1-1][3] = data_dict_minute[count1-1][-1][last_px]
                            
                            
                            #High
                            data_dict_minute_concat[count1-1][4] = maximum[last_px]
                            #Low
                            data_dict_minute_concat[count1-1][5] = minimum[last_px]

                            #twap
                            data_dict_minute_concat[count1-1][9] = List_twap
                            
                            
                        else:
                            pass
                        
                        #Amount&volume
                        if count1-2>=0:
                            data_dict_minute_concat[count1-1][6] = float(data_dict_minute[count1-1][-1][total_amount])-float(data_dict_minute[count1-2][-1][total_amount])
                            data_dict_minute_concat[count1-1][7] = float(data_dict_minute[count1-1][-1][total_volume])-float(data_dict_minute[count1-2][-1][total_volume])
                        
                        else:
                            pass
                        
                        
                        #Vwap
                        if data_dict_minute_concat[count1-1][7]!= 0:
                            data_dict_minute_concat[count1-1][8] = 0.01*data_dict_minute_concat[count1-1][6]/data_dict_minute_concat[count1-1][7]/2
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
def create_dict(w1,Contract, factor_number, l = li, l_factor = li_factors):
    columns_0 = list(w1.columns)
    dt = columns_0.index('dt')
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
        data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, data_dict_factor_concat, count, count1, count2, temp, bl, temp_row = calc(1, columns_0, data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, data_dict_factor_concat,factor_number, count, count1, count2, temp, bl, temp_row)
    data_dict_minute_0[len(data_dict_minute_0)-1] =  [i for i in data_dict_minute_0[len(data_dict_minute_0)-1] if i != 0]
    minute_0 = {}
    for item in list(data_dict_minute_0.keys()):               
        if len(data_dict_minute_0[item]) > 10 and data_dict_minute_0[item][0][dt][11:16] != '11:30':
            temp_key = data_dict_minute_0[item][0][dt][0:17]+'00'
            minute_0[temp_key] =  data_dict_minute_0[item]
    
    df_0 = pd.DataFrame(data_dict_minute_concat_0).T


    df_0.columns = l
 
    if df_0['dt'].iloc[0] == 0:
        df_0 = df_0.iloc[1:]

    df_0 = df_0[(df_0.T != 0).any()]
    
    df_0 = df_0.reset_index(drop = True)
    
    #df_0.to_csv('New/'+Contract+'/'+now)
    
    df_1 = pd.DataFrame(data_dict_factor_concat).T
    df_1.columns = l_factor
    if df_1['dt'].iloc[0] == 0:
        df_1 = df_1.iloc[1:]    
    
    df_1 = df_1[(df_1.T != 0).any()]
    df_1 = df_1.reset_index(drop = True)
    df_0 = df_0[df_0['dt'].str.contains(' 07:| 08:| 15:| 09:28') == False]
    df_1 = df_1[df_1['dt'].str.contains(' 07:| 08:| 15:| 09:28') == False]
 
    #df_1.to_csv('New/Factors/OrderFlowImbalance/'+Contract+'/'+now)
    
    return df_0, df_1, data_dict_0, data_dict_minute_0, data_dict_minute_concat_0, data_dict_factor_concat, minute_0 


df_s = pd.DataFrame()

factor_number = 19


def get_result(item):
    now = item
    if now in Contract_t_3:
        start = time.time()

        filename_2 = read_path + now

        w3 = pd.read_csv(filename_2)
        w3_30 = w3.copy()
        
        # time lags
        dt_list = pd.to_datetime(w3_30['dt'], format='%Y-%m-%d %H:%M:%S.%f')
        dt_list = dt_list - datetime.timedelta(seconds=tt)
        dt_list = dt_list.astype(str)
        w3_30['dt'] = dt_list
        
        columns_0_2 = list(w3.columns)
        
       
        for w in [w3_30]:   
            w['Volume'] = w['TotalVolumeTrade'].diff()
            w['Amount'] = w['TotalValueTrade'].diff()
            w['BidAskSpread'] = w['Sell1Price'] - w['Buy1Price']
            w['BidAskSpreadWeighted'] = w['BidAskSpread']*(w['Sell1OrderQty']+w['Buy1OrderQty'])
            w['OrderFlowImbalanceLv1'] = w['Buy1OrderQty'] - w['Sell1OrderQty']
            w['OrderFlowImbalanceRatioLv1'] = (w['Buy1OrderQty'] - w['Sell1OrderQty'])/(w['Buy1OrderQty'] + w['Sell1OrderQty'])


        w3['Name']=Contract_3
        w3_30['Name'] = Contract_3
        columns_0_2 = list(w3.columns)
        df_0, df, data_dict_0_2, data_dict_minute_0_2, data_dict_minute_concat_0_2, data_dict_factor_concat_0_2, minute_0_2 = create_dict(w3_30, Contract_3, factor_number)
         
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
            
            dt_list4 = pd.to_datetime(df['dt'], format='%Y-%m-%d %H:%M:%S.%f')
            dt_list4 = dt_list4 + datetime.timedelta(seconds=tt)
            if dt_list4.iloc[0].minute == 29:
                dt_list4.iloc[0] = dt_list4.iloc[0] + datetime.timedelta(seconds=(60-tt))
            df['dt'] = dt_list4
            df = df.set_index('dt')
        else:
            df_0['dt'] = pd.to_datetime(df_0['dt'], format='%Y-%m-%d %H:%M:%S.%f')
            df_0 = df_0.set_index('dt')
            df['dt'] = pd.to_datetime(df['dt'], format='%Y-%m-%d %H:%M:%S.%f')
            df = df.set_index('dt')
            
        df_s = pd.concat([df_0, df], axis = 1)
        i_list = list(df_s.index)
        i_list = [item for item in i_list if not ((item.hour == 11 and item.minute == 30) or (((item.hour ==9 and item.minute<30) or item.hour<9) or (item.hour == 14 and item.minute > 57) or item.hour >= 15))]
        df_s = df_s.loc[i_list]
        df_s.to_csv(save_path +'/' + now)
        print(time.time()-start)
        print(item)

with Pool(processes = 24) as pool:
    pool.map(get_result, Contract_t_3)
