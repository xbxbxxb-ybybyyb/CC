bar = 1

import sys
sys.path.insert(4, 'C:/Users/Beike_Auth/utils_all/')
import pandas as pd
import numpy as np
from operators_cc import *
from operators_wyc import *
from operators_wsc_1_0 import *
import datetime
import re, os, glob
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from multifactor.IO import IO
from tqdm import tqdm
from multiprocessing import Pool
import dill, functools
import shutil
import bottleneck as bk
import random
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from pandas.testing import assert_frame_equal, assert_series_equal
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

import gc
import pickle
from skimage.util import view_as_windows
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
from joblib import Parallel, delayed

def replace_zero(data, x=np.nan):
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal, must be pd.Series, pd.DataFrame or np.ndarray'
    if isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
    data[abs(data) < 1e-8] = x
    return data

cat_temp_list = ['AU.SHF',
 'OI.CZC',
 'PP.DCE',
 'SR.CZC',
 'NI.SHF',
 'SN.SHF',
 'ZN.SHF',
 'A.DCE',
 'AG.SHF',
 'Y.DCE',
 'SC.INE',
 'CU.SHF',
 'P.DCE',
 'AL.SHF',
 'CF.CZC',
 'EG.DCE',
 'SS.SHF',
 'EB.DCE',
 'M.DCE',
 'SM.CZC',
 'SF.CZC',
 'RU.SHF',
 'SP.SHF',
 'HC.SHF',
 'PG.DCE',
 'FU.SHF',
 'RM.CZC',
 'C.DCE',
 'PF.CZC',
 'AP.CZC',
 'L.DCE',
 'V.DCE',
 'TA.CZC',
 'JD.DCE',
 'J.DCE',
 'MA.CZC',
 'RB.SHF',
 'BU.SHF',
 'JM.DCE',
 'LH.DCE',
 'FG.CZC',
 'I.DCE',
 'SA.CZC',
 'EC.INE',
 'LC.GFE']


multiplier_dict = {
'LR.CZC': 20,
'BC.INE': 5,
'LU.INE':  10,
'NR.INE':  10,
'SC.INE':  1000,
'BB.DCE':  500,
'RI.CZC':  20,
'JR.CZC':  20,
'A.DCE':  10,
'AG.SHF':  15,
'AL.SHF':  5,
'AP.CZC':  10,
'AU.SHF':  1000,
'B.DCE':  10,
'BU.SHF':  10,
'C.DCE':  10,
'CF.CZC':  5,
'CJ.CZC':  5,
'CS.DCE':  10,
'CU.SHF':  5,
'CY.CZC':  5,
'EB.DCE':  5,
'EG.DCE':  10,
'FB.DCE':  10,
'FG.CZC':  20,
'FU.SHF':  10,
'HC.SHF':  10,
'I.DCE':  100,
'IC.CFE':  200,
'IF.CFE':  300,
'IH.CFE':  300,
'J.DCE':  100,
'JD.DCE':  10,
'JM.DCE':  60,
'L.DCE':  5,
'LH.DCE':  16,
'M.DCE':  10,
'MA.CZC':  10,
'NI.SHF':  1,
'OI.CZC':  10,
'P.DCE':  10,
'PB.SHF':  5,
'PF.CZC':  5,
'PG.DCE':  20,
'PK.CZC':  5,
'RS.CZC':  10,
'RU.SHF':  10,
'SA.CZC':  20,
'SF.CZC':  5,
'SM.CZC':  5,
'SN.SHF':  1,
'SP.SHF':  10,
'SR.CZC':  10,
'PM.CZC':  50,
'PP.DCE':  5,
'RB.SHF':  10,
'RM.CZC':  10,
'RR.DCE':  10,
'SS.SHF':  5,
'T.CFE':  10000,
'TL.CFE':  10000,
'TA.CZC':  5,
'TF.CFE':  10000,
'TS.CFE':  20000,
'UR.CZC':  20,
'V.DCE':  5,
'WH.CZC':  20,
'WR.SHF':  10,
'Y.DCE':  10,
'ZC.CZC':  100,
'ZN.SHF':  5,
'BR.SHF':  5,
'AO.SHF':  20,
'EC.INE':  50,
'PX.CZC':  5,
'SH.CZC':  30,
'IC.CFE': 200,
'IM.CFE': 200,
'IF.CFE': 300,
'IH.CFE': 300,
'SI.GFE': 5,
'LC.GFE': 1,
'PS.GFE':5,
'PR.CZC':15
}

ex_dict = {}
for cat in multiplier_dict.keys():
    ex_dict[cat.split('.')[0]] = cat
def get_prod_id(contract, ex_dict = ex_dict):
    cat = contract.replace('.csv', '')
    cl = [i for i in cat if not i.isdigit()]
    temp = ''
    for i in cl:
        temp = temp + str(i)
    return ex_dict[temp.upper()]

di_orders = {}
di_orders_temp = pd.read_pickle('E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/orders_div.pkl')      
for key in di_orders_temp:
    di_orders[key] = {}
    for key2 in di_orders_temp[key]:
        _df = di_orders_temp[key][key2].shift(1).rolling(5, min_periods = 1).mean()
        _df.iloc[0] = di_orders_temp[key][key2].iloc[0]
        di_orders[key][key2] = _df

make0nan_columns = ['open','high','low','close','twap','vwap','Buy1Price_mean','Sell1Price_mean']
ffill_columns = ['open','high','low','close','twap','vwap','Buy1Price_mean','Sell1Price_mean','HTSCSecurityID','Ticker', 'tday', 'oi']
fill0_columns = ['amount', 'OBI', 'Sell1OrderQty_mean', 'BidAskSpreadMean','PxVolCorr', 'volume', 'AbsPxPath',  'Buy1OrderQty_mean','first_10_volume', 'first_10_ret',
        'last_n_4_volume', 'last_n_4_ret','last_n_20_volume', 'last_n_20_ret', 'buy_active', 'sell_active', 'last_to_mid', 
        'last_to_weighted_mid', 'idmin', 'idmax', 'volume_after_min', 'volume_after_max', 
        'buy_big_volume', 'buy_big_count', 'sell_big_volume', 'sell_big_count', 'buy_super_volume', 
        'buy_super_count', 'sell_super_volume', 'sell_super_count', 'buy_small_volume', 'buy_small_count', 'sell_small_volume', 'sell_small_count',
        'buy_gigantic_volume', 'buy_gigantic_count', 'sell_gigantic_volume', 'sell_gigantic_count',
        'buy_big_volume_n_4', 'buy_big_count_n_4', 'sell_big_volume_n_4', 'sell_big_count_n_4', 
        'buy_big_volume_n_20', 'buy_big_count_n_20', 'sell_big_volume_n_20', 'sell_big_count_n_20', 
        'buy_super_volume_n_20', 'buy_super_count_n_20', 'sell_super_volume_n_20', 'sell_super_count_n_20', 'buy_small_volume_n_20', 'buy_small_count_n_20', 'sell_small_volume_n_20', 'sell_small_count_n_20',
        'buy_active_n_20', 'sell_active_n_20', 'last_to_mid_n_20', 'PxVolCorr_n_20', 
        'buy_gigantic_volume_n_20', 'buy_gigantic_count_n_20', 'sell_gigantic_volume_n_20', 'sell_gigantic_count_n_20',
                ]
fill02na_columns = ['open','high','low','close','twap','vwap']
rule_dict = {x:'last'  for x in ['open', 'high', 'low', 'close', 'twap', 'HTSCSecurityID',
        'volume', 'amount', 'AbsPxPath', 
       'OBI', 'BidAskSpreadMean',
       'Buy1Price_mean', 'Buy1OrderQty_mean', 'Sell1Price_mean',
       'Sell1OrderQty_mean', 'PxVolCorr', 'tday', 'oi',
         'buy_active', 'sell_active', 
        'first_10_volume', 'first_10_ret',
         'last_n_4_volume', 'last_n_4_ret', 'last_n_20_volume', 'last_n_20_ret', 'last_to_mid', 'last_to_weighted_mid', 'idmin', 'idmax', 
                                 'volume_after_min', 'volume_after_max', 
                                 'buy_big_volume', 'buy_big_count', 'sell_big_volume', 'sell_big_count', 
                                 'buy_super_volume', 'buy_super_count', 'sell_super_volume', 'sell_super_count',
                                 'buy_small_volume', 'buy_small_count', 'sell_small_volume', 'sell_small_count',
                                 'buy_gigantic_volume', 'buy_gigantic_count', 'sell_gigantic_volume', 'sell_gigantic_count',
                                 'buy_big_volume_n_4', 'buy_big_count_n_4', 'sell_big_volume_n_4', 'sell_big_count_n_4', 
                                 'buy_super_volume_n_4', 'buy_super_count_n_4', 'sell_super_volume_n_4', 'sell_super_count_n_4', 
                                 'buy_small_volume_n_4', 'buy_small_count_n_4', 'sell_small_volume_n_4', 'sell_small_count_n_4', 
                                 'buy_active_n_4', 'sell_active_n_4', 'last_to_mid_n_4', 'PxVolCorr_n_4',                      
                                 'buy_gigantic_volume_n_4', 'buy_gigantic_count_n_4', 'sell_gigantic_volume_n_4', 'sell_gigantic_count_n_4',
                                 'buy_big_volume_n_20', 'buy_big_count_n_20', 'sell_big_volume_n_20', 'sell_big_count_n_20', 
                                 'buy_super_volume_n_20', 'buy_super_count_n_20', 'sell_super_volume_n_20', 'sell_super_count_n_20', 'buy_small_volume_n_20', 'buy_small_count_n_20', 'sell_small_volume_n_20', 'sell_small_count_n_20',
                                 'buy_active_n_20', 'sell_active_n_20', 'last_to_mid_n_20', 'PxVolCorr_n_20', 
                                 'buy_gigantic_volume_n_20', 'buy_gigantic_count_n_20', 'sell_gigantic_volume_n_20', 'sell_gigantic_count_n_20' ]                   
            }
rule_dict.update({'open':'first','high':'max','low':'min','volume':'sum','amount':'sum'})
as_fl_list = ['PreOpenInterest', 'PreClosePx',
       'PreSettlePrice', 'OpenPx', 'HighPx', 'LowPx', 'LastPx',
       'TotalVolumeTrade', 'TotalValueTrade', 'OpenInterest', 'ClosePx',
       'Buy1Price',
       'Buy1OrderQty', 'Sell1Price', 'Sell1OrderQty']

def standard_index(data, ticker, night_end_time = None):
    t_days_list = udt.get_trading_date_range(str(data.index[0].date()).replace('-',''),str(data.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    
    if ticker in ['IC.CFE', 'IF.CFE', 'IH.CFE', 'IM.CFE']:
        t_mins_list = pd.date_range('09:30:00','11:29:00', freq='%smin'%bar).to_list() + pd.date_range('13:00:00','14:59:00', freq='%smin'%bar).to_list()
    elif ticker in ['T.CFE', 'TL.CFE', 'TS.CFE', 'TF.CFE']:
        t_mins_list = pd.date_range('09:30:00','11:29:00', freq='%smin'%bar).to_list() + pd.date_range('13:00:00','15:29:00', freq='%smin'%bar).to_list()
    else:
        t_mins_list = pd.date_range('09:00:00','10:14:00', freq='%smin'%bar).to_list() + pd.date_range('10:30:00','11:29:00', freq='%smin'%bar).to_list() + pd.date_range('13:30:00','14:59:00', freq='%smin'%bar).to_list()
    
    if night_end_time is None:
    
        t_mins_list = [str(i)[-8:] for i in t_mins_list]
        index_list = []
        for d in t_days_list:
            for m in t_mins_list:
                index_list.append(d + ' ' + m)
        index_df = pd.DataFrame({'dt':index_list})
        index_df['dt'] = pd.to_datetime(index_df['dt'])
        index_df = index_df.set_index('dt')
    
        data = index_df.join(data, how = 'left')
    
    else:
        netime = night_end_time[:2] + ':' + night_end_time[2:] + ':' + '00'
        t_days_pair = []
        for i, date in enumerate(t_days_list):
            if i > 0:
                t_days_pair.append([t_days_list[i-1], t_days_list[i]])
        if int(night_end_time) > 2100:
    
            last_list = pd.date_range('21:00:00',netime, freq='%smin'%bar).to_list()
            t_mins_list_0 = []
    
    
        else:
    
            last_list = pd.date_range('21:00:00','23:59:00', freq='%smin'%bar).to_list() 
            t_mins_list_0 =  pd.date_range('00:00:00',netime, freq='%smin'%bar).to_list()# + t_mins_list
    
        t_mins_list = [str(i)[-8:] for i in t_mins_list]
        t_mins_list_0 = [str(i)[-8:] for i in t_mins_list_0]
        last_list = [str(i)[-8:] for i in last_list]
    
        index_list = []
    
        
        for dpair in t_days_pair:
            lastd = dpair[0]
            d = dpair[1]
    
            fuck_date = str((pd.to_datetime(lastd) + pd.Timedelta(days = 1)).date())
            if ((pd.to_datetime(d) - pd.to_datetime(lastd)).total_seconds() / 86400 > 1) and (int(night_end_time) < 300) and (data.loc[fuck_date]['volume'].sum() > 0):
    
    
                for m in last_list:
                    index_list.append(lastd + ' ' + m)
                for m in t_mins_list_0:
                    index_list.append(fuck_date + ' ' + m)
                for m in t_mins_list:
                    index_list.append(d + ' ' + m)
            else:
    
                for m in last_list:
                    index_list.append(lastd + ' ' + m)
                for m in t_mins_list_0 + t_mins_list:
                    index_list.append(d + ' ' + m)
        index_df = pd.DataFrame({'dt':index_list})
        index_df['dt'] = pd.to_datetime(index_df['dt'])
        index_df = index_df.set_index('dt')
    
        data = index_df.join(data, how = 'left')
    return data
    

def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    else:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding
        
def chip_dis(price, volume, window1):
    if len(price) < window1:
        window = len(price)
    else:
        window = window1
    temp = rolling_window_upgrade(price.values, window)
    temp_amount = rolling_window_upgrade(volume.values, window)
    _r = ([np.nan] * (window - 1) + list(np.nansum([item < item[-1] for item in temp] * temp_amount, axis = 1))) /volume.rolling(window, min_periods = 1).sum().values
    return pd.Series(_r, index = price.index)  
    

       
    
def get_minute_data(path1):
    if 'MAIN' in path1:
        contract_kind = 'MAIN'
    if 'SECONDMAIN' in path1:
        contract_kind = 'SECONDMAIN'
    try:
        path = path1.replace("\\", '/')
        TDAY = int(path.split('/')[-1].split('.csv')[0])
        tick = pd.read_csv(path,  parse_dates=['dt'], index_col=['dt'])
        ticker = path.split('/')[-2]
        try:
            tick[as_fl_list] = tick[as_fl_list].astype(float)
        except Exception as e:
            print(path, e, '  astype error')
            
        tick['volume'] = tick['TotalVolumeTrade'].fillna(method = 'ffill').diff().fillna(tick['TotalVolumeTrade'])
        tick['amount'] = tick['TotalValueTrade'].fillna(method = 'ffill').diff().fillna(tick['TotalValueTrade'])
        
        tick = tick[(tick['LastPx'] < tick['PreClosePx'] * 1.3) & (tick['LastPx'] > tick['PreClosePx'] / 1.3) & \
            (tick['HighPx'] < tick['PreClosePx'] * 1.3) & (tick['HighPx'] > tick['PreClosePx'] / 1.3) & \
            (tick['LowPx']  < tick['PreClosePx'] * 1.3) & (tick['LowPx']  > tick['PreClosePx'] / 1.3) & \
            (tick['LowPx']  <= tick['HighPx']) & (tick['LowPx']  >= tick['HighPx'] / 1.6)
        ]  
        
        tick = tick[(tick['amount'] >= 0) & (tick['volume'] >= 0)]
        tick = tick[tick.OpenPx !=0]
        if len(tick) == 0:
            if ticker in cat_temp_list:
                print(path, '   no trade')
            return
        #tick['TotalValueTrade'].diff().plot()
        checkdf = tick.iloc[:100]
        openpx = checkdf['OpenPx'].mode()[0]
        preclosepx = checkdf['PreClosePx'].mode()[0]
        PreOpenInterest = checkdf['PreOpenInterest'].mode()[0]
    
        tick = tick[(tick['OpenPx'] == openpx) & (tick['PreClosePx'] == preclosepx) & (tick['PreOpenInterest'] == PreOpenInterest)]
    
        if ticker.endswith('CZC'):
            tick['amount'] = tick['amount'] * multiplier_dict.get(ticker, 1)
            
        tick = tick[(tick.TotalVolumeTrade != 0) & (tick.TotalValueTrade != 0)]
        if len(tick) == 0:
            return
        tick_vwap = tick['amount'] / tick['volume'] / multiplier_dict.get(ticker, 1)

        if '.CZC' in ticker:
            if (tick_vwap.iloc[:100].mean() / tick['LastPx'].iloc[:100].mean()) > (multiplier_dict.get(ticker, 1) / 2):
                tick['amount'] = tick['amount'] / multiplier_dict.get(ticker, 1)
                tick_vwap = tick['amount'] / tick['volume'] / multiplier_dict.get(ticker, 1)

        tick['tick_vwap'] = (tick['amount'] / replace_zero(tick['volume'].copy()) / multiplier_dict.get(ticker, 1)).fillna(method = 'ffill')
        #tick = tick[(tick_vwap < tick['PreClosePx'] * 1.3) & (tick_vwap < (tick['LastPx'] * 1.02)) & (tick_vwap > tick['PreClosePx'] / 1.3) & ((tick_vwap > tick['LastPx'] / 1.02))]
        
        
        if int(TDAY) == 20201111:
            pass
        else:
            if ('UpperLimitPx' in tick.columns) and ('LowerLimitPx' in tick.columns):
                if ticker.endswith('CZC'):
                    tick = tick[tick['LastPx'] <= (tick.UpperLimitPx)]
                    tick = tick[tick['LastPx'] >= (tick.LowerLimitPx)]
                else:
                    tick = tick[tick['tick_vwap'] <= (tick.UpperLimitPx)]
                    tick = tick[tick['tick_vwap'] >= (tick.LowerLimitPx)]
        _columns = [item for item in tick.columns if 'tick_vwap' not in item]
        tick = tick[_columns]
        tick.index = pd.to_datetime(tick.index, format='ISO8601')
        if tick['volume'].between_time('2100','0229').sum() > 0:
            tick = pd.concat([pd.DataFrame(index = [tick.index[0].replace(hour = 19)]), tick])
        else:
            tick = pd.concat([pd.DataFrame(index = [tick.index[0].replace(hour = 7)]), tick])
            
        tick = pd.concat([tick, pd.DataFrame(index = [tick.index[-1].replace(hour = 16)])])
        tick.index.name = 'dt'
        tick = tick.sort_index().reset_index()
        
        
        
        fill_na_columns = ['Buy1Price','Sell1Price','LastPx']
        tick[fill_na_columns] =  tick[fill_na_columns].replace(0,np.nan)
        
        tick['Sell1Price'] = tick['Sell1Price'].astype(float)
        tick['Buy1Price'] = tick['Buy1Price'].astype(float)
    
        tick['Sell1Price'][(tick['Sell1Price'] == 0) ] = np.nan
        tick['Buy1Price'][(tick['Buy1Price'] == 0) ] = np.nan
        tick['Buy1Price'][(tick['Buy1Price'] > tick['Sell1Price']) & (~np.isnan(tick['Sell1Price']))] = np.nan
        tick['pd'] = tick['OpenInterest'].diff()
    
        med = tick['LastPx'].copy()
        tick['Sell1Price'][tick['Sell1Price'] > (med * 1.1)] = np.nan
        tick['Sell1Price'][tick['Sell1Price'] < (med / 1.1)] = np.nan
        tick['Buy1Price'][tick['Buy1Price'] > (med * 1.1)] = np.nan
        tick['Buy1Price'][tick['Buy1Price'] < (med / 1.1)] = np.nan
    
        #tick['Buy1Price'] = tick['Buy1Price'].fillna(tick['Sell1Price'])
        #tick['Sell1Price'] = tick['Sell1Price'].fillna(tick['Buy1Price'])
        
    
        midprice = pd.concat([tick['Sell1Price'], tick['Buy1Price']], axis = 1).mean(axis = 1)
        midprice = midprice.fillna(method = 'ffill')
    
        tick_vwap = tick['amount'] / tick['volume'] / multiplier_dict.get(ticker, 1)
        
        mean_mid =  midprice.mean()
        mean_vwap = tick_vwap.mean()
    
        if (np.isnan(mean_vwap)) & (np.isnan(mean_mid)):
            tick_vwap = tick['LastPx'].copy()
            midprice = tick['LastPx'].copy()
        elif (np.isnan(mean_vwap)) & (~np.isnan(mean_mid)):
            tick_vwap = midprice.copy()
        elif (~np.isnan(mean_vwap)) & (np.isnan(mean_mid)):
            midprice = tick_vwap.copy()
        assert abs(tick_vwap.mean() / midprice.mean() - 1) < 0.2,  path
        
        if ('20190425' in path) or ('20190426' in path) or ('20201111' in path) or ('2024' in path):
            zt_flag =  (tick['Sell1OrderQty'] == 0) & (tick['LastPx'] == tick['HighPx']) & ((tick['Sell1Price'] == 0) | tick['Sell1Price'].isna())
            dt_flag =  (tick['Buy1OrderQty'] == 0) & (tick['LastPx'] == tick['LowPx']) & ((tick['Buy1Price'] == 0) | tick['Buy1Price'].isna())
        else:
            zt_flag = (tick['LastPx'] == tick['UpperLimitPx'])
            dt_flag = (tick['LastPx'] == tick['LowerLimitPx'])
        
        if ticker.endswith('CZC'):
            # Lee-Ready
            tick['zbuy'] = ((tick['LastPx'] > midprice) | ((tick['LastPx'] == midprice) &  (tick['LastPx'] > tick['LastPx'].shift(1))) | ((tick['LastPx'] == tick['LastPx'].shift(1)) & (dt_flag.astype(int) == True))) * tick['volume']
            tick['zsell'] = ((tick['LastPx'] < midprice) | ((tick['LastPx'] == midprice) &  (tick['LastPx'] < tick['LastPx'].shift(1))) |((tick['LastPx'] == tick['LastPx'].shift(1)) & (zt_flag.astype(int) == True))) * tick['volume']
        else:
            # self-made
            tick['zbuy'] = ((tick_vwap > midprice.shift(1)) | ((tick_vwap == midprice.shift(1)) & (dt_flag.astype(int) == True))) * tick['volume']
            tick['zsell'] = ((tick_vwap < midprice.shift(1)) | ((tick_vwap == midprice.shift(1)) & (zt_flag.astype(int) == True))) * tick['volume']
        
        
        #tick['trade_will'] = (tick['volume'] / r(tick['Buy1OrderQty'].shift(1) + tick['Sell1OrderQty'].shift(1)))
        tick['minute'] = tick.dt.map(lambda x: x.replace(second=0, microsecond = 0))
        tick = tick.set_index('dt')
        tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
        tick['pricediff'] = abs(tick.LastPx.diff())
        tick[['Buy1Price','Buy1OrderQty']] = tick[['Buy1Price','Buy1OrderQty']].astype('float64')
    
    
        tick['BidAskSpreadMean'] = tick['Sell1Price'] - tick['Buy1Price']
        tick['BidAskSpreadMean'][tick['BidAskSpreadMean'] == tick['Sell1Price']] = np.nan
        tick['BidAskSpreadMean'][tick['BidAskSpreadMean'] == -tick['Buy1Price']] = np.nan
        for x in ['open','high','low','close','twap']:
            tick[x] = tick['LastPx']
        for x in ['Buy1Price','Buy1OrderQty','Sell1Price','Sell1OrderQty']:
            tick['%s_mean' % x] = tick[x]
    
        aggdict_ohlc = {'open':'first','high':'max','low':'min','close':'last','twap':'mean'}
    
    
        tick['n_min'] = tick.index.floor(f'{bar}T')
        tick['is_first_10s'] = (tick.index - tick['n_min']) <= pd.Timedelta('10s')
        
        zbuy = tick.groupby('n_min')['zbuy'].sum()
        zsell = tick.groupby('n_min')['zsell'].sum()
        #trade_will.name = 'trade_will'
        zbuy.name = 'buy_active'
        zsell.name = 'sell_active'
        
        order_df = di_orders[ticker][contract_kind]
        _zbuy_temp = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['big']) & (tick['zbuy'] <= order_df.loc[str(TDAY)]['super'])].groupby('n_min')
        _zsell_temp = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['big']) & (tick['zsell'] <= order_df.loc[str(TDAY)]['super'])].groupby('n_min')
        big_buy = _zbuy_temp['zbuy'].sum()
        big_sell = _zsell_temp['zsell'].sum()
        
        
        big_buy_count = _zbuy_temp['zbuy'].count()
        big_sell_count = _zsell_temp['zsell'].count()
        
        big_sell.name = 'sell_big_volume'
        big_sell_count.name = 'sell_big_count'
        
        big_buy.name = 'buy_big_volume'
        big_buy_count.name = 'buy_big_count'
    
        del _zbuy_temp
        del _zsell_temp
        _zbuy_temp = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['super']) & (tick['zbuy'] <= order_df.loc[str(TDAY)]['gigantic'])].groupby('n_min')
        _zsell_temp = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['super']) & (tick['zsell'] <= order_df.loc[str(TDAY)]['gigantic'])].groupby('n_min')
        
        super_buy = _zbuy_temp['zbuy'].sum()
        super_sell = _zsell_temp['zsell'].sum()
    
    
        super_buy_count = _zbuy_temp['zbuy'].count()
        super_sell_count = _zsell_temp['zsell'].count()
    
        super_sell.name = 'sell_super_volume'
        super_sell_count.name = 'sell_super_count'
    
        super_buy.name = 'buy_super_volume'
        super_buy_count.name = 'buy_super_count'
        del _zbuy_temp
        del _zsell_temp
    
        _zbuy_temp = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['gigantic'])].groupby('n_min')
        _zsell_temp = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['gigantic'])].groupby('n_min')
        
        gigantic_buy = _zbuy_temp['zbuy'].sum()
        gigantic_sell = _zsell_temp['zsell'].sum()
        
        
        gigantic_buy_count = _zbuy_temp['zbuy'].count()
        gigantic_sell_count = _zsell_temp['zsell'].count()
        
        gigantic_sell.name = 'sell_gigantic_volume'
        gigantic_sell_count.name = 'sell_gigantic_count'
        
        gigantic_buy.name = 'buy_gigantic_volume'
        gigantic_buy_count.name = 'buy_gigantic_count'
        del _zbuy_temp
        del _zsell_temp
        
        _zbuy_temp = tick[tick['zbuy'] <= np.nanmax([order_df.loc[str(TDAY)]['small'], 1])].groupby('n_min')
        _zsell_temp = tick[tick['zsell'] <= np.nanmax([order_df.loc[str(TDAY)]['small'], 1])].groupby('n_min')
        small_buy = _zbuy_temp['zbuy'].sum()
        small_sell = _zsell_temp['zsell'].sum()
    
    
        small_buy_count = _zbuy_temp['zbuy'].count()
        small_sell_count = _zsell_temp['zsell'].count()
    
        small_sell.name = 'sell_small_volume'
        small_sell_count.name = 'sell_small_count'
    
        small_buy.name = 'buy_small_volume'
        small_buy_count.name = 'buy_small_count'
        
        pvcorrdf = tick[['n_min','LastPx','volume']].groupby('n_min').corr().xs('LastPx', level = 1)[['volume']]
        pvcorrdf.columns = ['PxVolCorr']
    
        # 计算每个n分钟时间段内前10秒的成交量平均值
        group_10s = tick[tick['is_first_10s']].groupby('n_min')
        
        first_10s_volume_mean = group_10s['volume'].sum()
        first_10s_ret = group_10s['LastPx'].last() - group_10s['LastPx'].first()
    
    
        first_10s_volume_mean.name = 'first_10_volume'
        first_10s_ret.name = 'first_10_ret'
    
    
        df_temp1 = pd.concat([first_10s_volume_mean,  first_10s_ret], axis = 1)
        
        tick['midprice'] = pd.concat([tick['Sell1Price'], tick['Buy1Price']], axis = 1).mean(axis = 1)
        tick['weighted_mid'] = ((tick['Sell1Price'] * tick['Sell1OrderQty']) + (tick['Buy1Price'] * tick['Buy1OrderQty'])) / r(tick['Sell1OrderQty'] + tick['Buy1OrderQty'])
        
        tick['last_to_mid'] = (tick['LastPx'] - tick['midprice'])
        tick['last_to_weighted_mid'] = tick['LastPx'] - tick['weighted_mid']
        tick['last_to_mid'][tick['last_to_mid']>(tick['LastPx']*0.02)]= np.nan
        tick['last_to_weighted_mid'][tick['last_to_weighted_mid']>(tick['LastPx']*0.02)]= np.nan
        # 计算每个n分钟内的总成交量
        total_volume = tick.groupby('n_min')['volume'].sum()
        total_volume.name = 'total_volume'
        # 计算每个n分钟内最后n/4时间内的成交量
        # 0.75分钟 = 45秒
        tick['is_last_n_4'] = (tick.index - tick['n_min']) >= pd.Timedelta(f'{bar * 3 / 4}T')
        # 确保每个n分钟的第一条记录不会被错误地算到前一个n分钟的最后n/4时间段内
        tick['is_first_in_n_min'] = tick['n_min'] != tick['n_min'].shift(1)
        
        # 计算每个n分钟内最后n/4时间内的成交量
        group_temp = tick[(tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        last_n_4_volume =group_temp['volume'].sum()
        last_n_4_volume.name = 'last_n_4_volume'
        last_n_4_ret = group_temp['LastPx'].last() - group_temp['LastPx'].first()
        last_n_4_ret.name = 'last_n_4_ret'
    
        zbuy_n_4 = group_temp['zbuy'].sum()
        zsell_n_4 = group_temp['zsell'].sum()
        #trade_will.name = 'trade_will'
        zbuy_n_4.name = 'buy_active_n_4'
        zsell_n_4.name = 'sell_active_n_4'
        
        last_to_mid_n_4 = group_temp['last_to_mid'].mean()
        last_to_mid_n_4.name = 'last_to_mid_n_4'
    
        _zbuy_temp2 = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['big']) & (tick['zbuy'] <= order_df.loc[str(TDAY)]['super']) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['big']) & (tick['zsell'] <= order_df.loc[str(TDAY)]['super']) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        big_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        big_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        
        big_buy_count_n_4 = _zbuy_temp2['zbuy'].count()
        big_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        big_sell_n_4.name = 'sell_big_volume_n_4'
        big_sell_count_n_4.name = 'sell_big_count_n_4'
        
        big_buy_n_4.name = 'buy_big_volume_n_4'
        big_buy_count_n_4.name = 'buy_big_count_n_4'
    
        del _zbuy_temp2
        del _zsell_temp2
        _zbuy_temp2 = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['super']) & (tick['zbuy'] <= order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['super']) & (tick['zsell'] <= order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        
        super_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        super_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        
        super_buy_count_n_4 =  _zbuy_temp2['zbuy'].count()
        super_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        super_sell_n_4.name = 'sell_super_volume_n_4'
        super_sell_count_n_4.name = 'sell_super_count_n_4'
        
        super_buy_n_4.name = 'buy_super_volume_n_4'
        super_buy_count_n_4.name = 'buy_super_count_n_4'
        
        del _zbuy_temp2
        del _zsell_temp2
    
        _zbuy_temp2 = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        
        gigantic_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        gigantic_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        
        gigantic_buy_count_n_4 =  _zbuy_temp2['zbuy'].count()
        gigantic_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        gigantic_sell_n_4.name = 'sell_gigantic_volume_n_4'
        gigantic_sell_count_n_4.name = 'sell_gigantic_count_n_4'
        
        gigantic_buy_n_4.name = 'buy_gigantic_volume_n_4'
        gigantic_buy_count_n_4.name = 'buy_gigantic_count_n_4'
        
        del _zbuy_temp2
        del _zsell_temp2
        
        _zbuy_temp2 = tick[(tick['zbuy'] <= np.nanmax([order_df.loc[str(TDAY)]['small'], 1])) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] <= np.nanmax([order_df.loc[str(TDAY)]['small'], 1])) & (tick['is_last_n_4']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        small_buy_n_4 = _zbuy_temp2['zbuy'].sum()
        small_sell_n_4 = _zsell_temp2['zsell'].sum()
        
        
        small_buy_count_n_4 = _zbuy_temp2['zbuy'].count()
        small_sell_count_n_4 = _zsell_temp2['zsell'].count()
        
        small_sell_n_4.name = 'sell_small_volume_n_4'
        small_sell_count_n_4.name = 'sell_small_count_n_4'
        
        small_buy_n_4.name = 'buy_small_volume_n_4'
        small_buy_count_n_4.name = 'buy_small_count_n_4'
        
        pvcorrdf_n_4 = tick[(tick['is_last_n_4']) & (~tick['is_first_in_n_min'])][['n_min','LastPx','volume']].groupby('n_min').corr().xs('LastPx', level = 1)[['volume']]
        pvcorrdf_n_4.columns = ['PxVolCorr_n_4']
        
        df_temp1 = pd.concat([df_temp1, last_n_4_volume, last_n_4_ret], axis = 1)
    
        
        
        
        '''
        # 分别计算每个价格上的买单和卖单数量
        buy_tick = tick[tick['zbuy'] > 0].groupby(['n_min', 'LastPx'])['volume'].sum().reset_index(name='buy_volume')
        sell_tick = tick[tick['zsell'] > 0].groupby(['n_min', 'LastPx'])['volume'].sum().reset_index(name='sell_volume')
        # 合并买单和卖单数据
        merged_tick = pd.merge(buy_tick, sell_tick, on=['n_min', 'LastPx'], how='outer').fillna(0)#.sort_values(by = 'LastPx')
        merged_tick['total'] = merged_tick['buy_volume'].fillna(0) + merged_tick['sell_volume'].fillna(0)
        # 筛选出买单数量大于卖单数量三倍的行
        filtered_tick_buy = merged_tick[merged_tick['buy_volume'] > 3 * merged_tick['sell_volume']]
        filtered_tick_sell = merged_tick[merged_tick['sell_volume'] > 3 * merged_tick['buy_volume']]
        
    
        # 计算每个时间段内符合条件的价格数量
        buy_imb_count = filtered_tick_buy.groupby('n_min').size().reset_index(name='count').set_index('n_min').fillna(0)
        sell_imb_count = filtered_tick_sell.groupby('n_min').size().reset_index(name='count').set_index('n_min').fillna(0)
        max_volume_price = merged_tick.set_index('LastPx').groupby('n_min')['total'].idxmax()
        max_volume = merged_tick.set_index('LastPx').groupby('n_min')['total'].max()
        
        buy_imb_count.columns = ['buy_imb_count']
        sell_imb_count.columns =['sell_imb_count']
        max_volume_price.name = 'max_volume_price'
        max_volume.name = 'max_volume'
        
        trade_will = tick.groupby('n_min')['trade_will'].mean()
        '''
        
        tick['is_last_n_20'] = (tick.index - tick['n_min']) >= pd.Timedelta(f'{bar * 19 / 20}T')
        # 确保每个n分钟的第一条记录不会被错误地算到前一个n分钟的最后n/4时间段内
        tick['is_first_in_n_min'] = tick['n_min'] != tick['n_min'].shift(1)
    
        # 计算每个n分钟内最后n/4时间内的成交量
        group_temp10 = tick[(tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        last_n_20_volume = group_temp10['volume'].sum()
        last_n_20_ret = group_temp10['LastPx'].last() - group_temp10['LastPx'].first()
        
        last_n_20_volume.name = 'last_n_20_volume'
        last_n_20_ret.name = 'last_n_20_ret'
        
        df_temp1 = pd.concat([df_temp1, last_n_20_volume, last_n_20_ret], axis = 1)
      
        zbuy_n_20 = group_temp10['zbuy'].sum()
        zsell_n_20 = group_temp10['zsell'].sum()
        #trade_will.name = 'trade_will'
        zbuy_n_20.name = 'buy_active_n_20'
        zsell_n_20.name = 'sell_active_n_20'
        
        last_to_mid_n_20 = group_temp10['last_to_mid'].mean()
        last_to_mid_n_20.name = 'last_to_mid_n_20'
        
        _zbuy_temp2 = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['big']) & (tick['zbuy'] <= order_df.loc[str(TDAY)]['super']) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['big']) & (tick['zsell'] <= order_df.loc[str(TDAY)]['super']) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        big_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        big_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        big_buy_count_n_20 = _zbuy_temp2['zbuy'].count()
        big_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        big_sell_n_20.name = 'sell_big_volume_n_20'
        big_sell_count_n_20.name = 'sell_big_count_n_20'
        
        big_buy_n_20.name = 'buy_big_volume_n_20'
        big_buy_count_n_20.name = 'buy_big_count_n_20'
        
        del _zbuy_temp2
        del _zsell_temp2
        _zbuy_temp2 = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['super']) & (tick['zbuy'] <= order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['super']) & (tick['zsell'] <= order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        
        super_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        super_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        super_buy_count_n_20 =  _zbuy_temp2['zbuy'].count()
        super_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        super_sell_n_20.name = 'sell_super_volume_n_20'
        super_sell_count_n_20.name = 'sell_super_count_n_20'
        
        super_buy_n_20.name = 'buy_super_volume_n_20'
        super_buy_count_n_20.name = 'buy_super_count_n_20'
        
        del _zbuy_temp2
        del _zsell_temp2
        
        _zbuy_temp2 = tick[(tick['zbuy'] > order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] > order_df.loc[str(TDAY)]['gigantic']) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        
        gigantic_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        gigantic_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        gigantic_buy_count_n_20 =  _zbuy_temp2['zbuy'].count()
        gigantic_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        gigantic_sell_n_20.name = 'sell_gigantic_volume_n_20'
        gigantic_sell_count_n_20.name = 'sell_gigantic_count_n_20'
        
        gigantic_buy_n_20.name = 'buy_gigantic_volume_n_20'
        gigantic_buy_count_n_20.name = 'buy_gigantic_count_n_20'
    
        _zbuy_temp2 = tick[(tick['zbuy'] <= np.nanmax([order_df.loc[str(TDAY)]['small'], 1])) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        _zsell_temp2 = tick[(tick['zsell'] <= np.nanmax([order_df.loc[str(TDAY)]['small'], 1])) & (tick['is_last_n_20']) & (~tick['is_first_in_n_min'])].groupby('n_min')
        small_buy_n_20 = _zbuy_temp2['zbuy'].sum()
        small_sell_n_20 = _zsell_temp2['zsell'].sum()
        
        
        small_buy_count_n_20 = _zbuy_temp2['zbuy'].count()
        small_sell_count_n_20 = _zsell_temp2['zsell'].count()
        
        small_sell_n_20.name = 'sell_small_volume_n_20'
        small_sell_count_n_20.name = 'sell_small_count_n_20'
        
        small_buy_n_20.name = 'buy_small_volume_n_20'
        small_buy_count_n_20.name = 'buy_small_count_n_20'
        
        pvcorrdf_n_20 = tick[(tick['is_last_n_20']) & (~tick['is_first_in_n_min'])][['n_min','LastPx','volume']].groupby('n_min').corr().xs('LastPx', level = 1)[['volume']]
        pvcorrdf_n_20.columns = ['PxVolCorr_n_20']
        
        '''
        bid_sub_price = tick['Buy1Price'] - tick['Buy1Price'].shift(1) 
        ask_sub_price = tick['Sell1Price'] - tick['Sell1Price'].shift(1)
        bid_sub_volume = tick['Buy1OrderQty'] - tick['Buy1OrderQty'].shift(1) 
        ask_sub_volume = tick['Sell1OrderQty'] - tick['Sell1OrderQty'].shift(1) 
        bid_volume_change = bid_sub_volume 
        ask_volume_change = ask_sub_volume 
        bid_volume_change[bid_sub_price == 0] = bid_sub_volume[bid_sub_price == 0] 
        bid_volume_change[bid_sub_price < 0] = 0 
        bid_volume_change[bid_sub_price > 0] = tick['Buy1OrderQty'][bid_sub_price > 0] 
        ask_volume_change[ask_sub_price < 0] = tick['Sell1OrderQty'][ask_sub_price < 0] 
        ask_volume_change[ask_sub_price > 0] = 0 
        voi = (bid_volume_change - ask_volume_change) / r(tick['volume'].copy())
        
    
        bid_p_previous = tick['Buy1OrderQty'].shift(1)
        bid_p_current = tick['Buy1OrderQty']
        # 当前bid price大于上一刻的bid price,增量为当前的挂单量也就是Buy1OrderQty
        delta_v1 = (bid_p_current > bid_p_previous) * tick['Buy1OrderQty']
        # 当前bid price小于上一刻的bid price,增量为前一刻被成交的量取负数
        delta_v2 = (bid_p_current < bid_p_previous) * tick['Buy1OrderQty'].shift(1) * -1.
        # 当前bid price等于上一刻的bid price,增量为当前的挂单量减去前一刻的挂单量
        delta_v3 = (bid_p_current == bid_p_previous) * (tick['Buy1OrderQty'] - tick['Buy1OrderQty'].shift(1))
        # 三者相加，得到最终的delta_v
        delta_Buy1OrderQty = delta_v1 + delta_v2 + delta_v3
        # 计算ask一侧
        ask_p_previous = tick['Sell1OrderQty'].shift(1)
        ask_p_current = tick['Sell1OrderQty']
        # 当前ask price大于上一刻的ask price,增量为前一刻被成交量取负数
        delta_v1 = (ask_p_current > ask_p_previous) * tick['Sell1OrderQty'].shift(1) * -1.
        # 当前aid price小于上一刻的aid price,增量为当前的挂单量也就是Buy1OrderQty
        delta_v2 = (ask_p_current < ask_p_previous) * tick['Sell1OrderQty'].shift(1) * -1.
        # 当前ask price等于上一刻的ask price,增量为当前的挂单量减去前一刻的挂单量
        delta_v3 = (ask_p_current == ask_p_previous) * (tick['Sell1OrderQty'] - tick['Sell1OrderQty'].shift(1))
        # 三者相加，得到最终的delta_v
        delta_Sell1OrderQty = delta_v1 + delta_v2 + delta_v3
        iof = (delta_Buy1OrderQty - delta_Sell1OrderQty) / r(delta_Buy1OrderQty + delta_Sell1OrderQty)
        
        
        tick['voi'] = voi
        tick['iof'] = iof
        
        tick['slope'] = (tick['Sell1Price'] - tick['Buy1Price']) / r(tick['Sell1OrderQty'] + tick['Buy1OrderQty'])
        voi_mean = grouped3['voi'].mean()
        iof_mean = grouped3['iof'].mean()
        slope_mean = grouped3['slope'].mean()
        slope_mean.name = 'slope'
        '''
        
        grouped3 = tick.groupby('n_min')
        last_to_mid = grouped3['last_to_mid'].mean()
        last_to_weighted_mid = grouped3['last_to_weighted_mid'].mean()
        
        
        last_to_mid.name = 'last_to_mid'
        last_to_weighted_mid.name = 'last_to_weighted_mid'
        
        
        
        temp_idxmin = (grouped3['LastPx'].idxmin() - grouped3['LastPx'].first().index)#.to_frame()
        idmin = temp_idxmin.apply(lambda x: x.total_seconds())
        temp_idxmax = (grouped3['LastPx'].idxmax() - grouped3['LastPx'].first().index)#.to_frame()
        idmax = temp_idxmax.apply(lambda x: x.total_seconds())
        
        result_idmin = []
        result_idmax = []
        for group_time, group_data in grouped3:
            result_idmax.append([group_time, (((group_data.index >= grouped3['LastPx'].idxmax().loc[group_time]).astype(int)) * group_data['volume']).sum()])
            result_idmin.append([group_time, (((group_data.index >= grouped3['LastPx'].idxmin().loc[group_time]).astype(int)) * group_data['volume']).sum()])
        idmin_volume = pd.DataFrame(result_idmin).set_index(0).iloc[:, 0]
        idmin_volume.index.name = 'dt'
        
        idmax_volume = pd.DataFrame(result_idmax).set_index(0).iloc[:, 0]
        idmax_volume.index.name = 'dt'
        
        idmin.name = 'idmin'
        idmax.name = 'idmax'
        idmin_volume.name = 'volume_after_min'
        idmax_volume.name = 'volume_after_max'
        
    
        df_temp1 = pd.concat([df_temp1, zbuy, zsell, last_to_mid, last_to_weighted_mid, idmin, idmin_volume, idmax, idmax_volume, big_buy, big_sell, big_buy_count, big_sell_count, super_buy, super_sell, super_buy_count, super_sell_count, small_buy, small_sell, small_buy_count, small_sell_count], axis = 1)
        df_temp1 = pd.concat([df_temp1, gigantic_buy, gigantic_sell, gigantic_buy_count, gigantic_sell_count], axis = 1)
        df_temp1 = pd.concat([df_temp1, big_buy_n_4, big_sell_n_4, big_buy_count_n_4, big_sell_count_n_4, super_buy_n_4, super_sell_n_4, super_buy_count_n_4, super_sell_count_n_4, small_buy_n_4, small_sell_n_4, small_buy_count_n_4, small_sell_count_n_4, zbuy_n_4, zsell_n_4, last_to_mid_n_4, pvcorrdf_n_4], axis = 1)
        df_temp1 = pd.concat([df_temp1, gigantic_buy_n_4, gigantic_sell_n_4, gigantic_buy_count_n_4, gigantic_sell_count_n_4], axis = 1)
        df_temp1 = pd.concat([df_temp1, big_buy_n_20, big_sell_n_20, big_buy_count_n_20, big_sell_count_n_20, super_buy_n_20, super_sell_n_20, super_buy_count_n_20, super_sell_count_n_20, small_buy_n_20, small_sell_n_20, small_buy_count_n_20, small_sell_count_n_20, zbuy_n_20, zsell_n_20, last_to_mid_n_20, pvcorrdf_n_20], axis = 1)
        df_temp1 = pd.concat([df_temp1, gigantic_buy_n_20, gigantic_sell_n_20, gigantic_buy_count_n_20, gigantic_sell_count_n_20], axis = 1)
        aggdict = {'HTSCSecurityID':'last', 'volume':'sum','amount':'sum','pricediff':'sum','OBI':'mean','BidAskSpreadMean':'mean'}
    
        agg_dict_v3 = {'Buy1Price_mean':'mean','Buy1OrderQty_mean':'mean','Sell1Price_mean':'mean','Sell1OrderQty_mean':'mean','HTSCSecurityID':'last', 'OpenInterest':'last'}
        agg_dict_v4 = {'TradingDate':'last'}
    
        df1amt = tick.resample('%smin'%str(bar)).agg({**aggdict_ohlc, **aggdict, **agg_dict_v3, **agg_dict_v4})
    
        renamedict1 = {'pricediff':'AbsPxPath', 'OpenInterest':'oi', 'TradingDate':'tday'}
        df1amt = df1amt.rename(columns = {**renamedict1})
    
        tickdf = df1amt.join(pvcorrdf).join(df_temp1)
        TDAY = int(path.split('/')[-1].split('.csv')[0])
        try:
            tickdf['tday'] = TDAY
        except:
            print('tday_error')
        
        morning_auction = tickdf.between_time('0858','0900')
        morning_auction = morning_auction.groupby(morning_auction.index.date).agg(rule_dict)
        morning_auction.index = [pd.to_datetime(str(x) + ' 090000') for x in morning_auction.index]
        if tickdf.between_time('1016','1028')['volume'].sum() > 0:
            tickdf_daily = pd.concat([tickdf.between_time('0901','1129'),tickdf.between_time('1300','1529'),morning_auction])
        else:
            tickdf_daily = pd.concat([tickdf.between_time('0901','1014'),tickdf.between_time('1030','1129'),tickdf.between_time('1300','1529'),morning_auction])
        
        night_end_time = None
        if tickdf.between_time('2102','2259').volume.sum() > 0:
            night_end_time = '2259'
        if tickdf.between_time('2302','2329').volume.sum() > 0:
            night_end_time = '2329'
        if tickdf.between_time('2332','2359').volume.sum() > 0:
            night_end_time = '2359'
        if tickdf.between_time('0002','0029').volume.sum() > 0:
            night_end_time = '0029'
        if tickdf.between_time('0032','0059').volume.sum() > 0:
            night_end_time = '0059'
        if tickdf.between_time('0102','0129').volume.sum() > 0:
            night_end_time = '0129'
        if tickdf.between_time('0132','0159').volume.sum() > 0:
            night_end_time = '0159'
        if tickdf.between_time('0202','0229').volume.sum() > 0:
            night_end_time = '0229'
            
            
        
        if night_end_time is not None:
            night_auction = tickdf.between_time('2058','2100')
            night_auction = night_auction.groupby(night_auction.index.date).agg(rule_dict)
            night_auction.index = [pd.to_datetime(str(x) + ' 210000') for x in night_auction.index]
            tickdf_daily = pd.concat([tickdf_daily,night_auction,tickdf.between_time('2101',night_end_time)])
        tickdf_daily.loc[tickdf_daily.volume < 0, 'volume'] = 0
        tickdf_daily['vwap'] = tickdf_daily['amount'] / tickdf_daily['volume'] / multiplier_dict.get(ticker, 1)
        tickdf_daily.loc[abs(tickdf_daily['vwap'] / tickdf_daily['twap'] - 1) > 0.3,'vwap'] = tickdf_daily['twap']
        tickdf_daily['Ticker'] = ticker
        tickdf_daily = tickdf_daily.sort_index().replace([np.inf,-np.inf],np.nan)
        tickdf_daily['tday'] = TDAY
        tickdf_daily.index.name = 'dt'
        tickdf_daily = standard_index(tickdf_daily, ticker, night_end_time)
        tickdf_daily[make0nan_columns] = tickdf_daily[make0nan_columns].replace([0],np.nan)
        tickdf_daily[ffill_columns] = tickdf_daily[ffill_columns].fillna(method = 'ffill')
        tickdf_daily[fill0_columns] = tickdf_daily[fill0_columns].fillna(value = 0)
        
        tickdf_daily['Ticker'] = ticker
        tickdf_daily['HTSCSecurityID'] = tick['HTSCSecurityID'].dropna().iloc[0]
        # tickdf_daily[['HTSCSecurityID','Ticker']] = tickdf_daily[['HTSCSecurityID','Ticker']].fillna(method = 'bfill')
        ffill_columns_new = ['open','high','low','close','twap','vwap','HTSCSecurityID','Ticker', 'tday', 'oi']
        tickdf_daily[ffill_columns_new] = tickdf_daily[ffill_columns_new].fillna(value = tick['PreClosePx'].dropna().iloc[0])
        tickdf_daily[fill0_columns] = tickdf_daily[fill0_columns].fillna(value = 0)
        try:
            tickdf_daily['tday'] = tickdf_daily['tday'].astype(int)#.astype(str)
        except:
            pass
        tickdf_daily[make0nan_columns] = tickdf_daily[make0nan_columns].replace([0],np.nan)
            
        
        if '1901' in path:
            save_pickle([TDAY, ticker], 'E:warehouse/prod/MD/CHINA_COMMODITY/records/%s_%s.pkl'%(TDAY, ticker))
        tickdf_daily = tickdf_daily[[col for col in tickdf_daily.columns if col != 'vwap']]
        return tickdf_daily.reset_index().set_index(['dt','Ticker'])
    except Exception as e:
        
        path = path1.replace("\\", '/')
        TDAY = int(path.split('/')[-1].split('.csv')[0])
        ticker = path.split('/')[-2]
        save_pickle([path1], 'E:/warehouse/prod/MD/CHINA_COMMODITY/error_records/%s_%s_%s.pkl'%(ticker, TDAY, contract_kind))

def handel_prod_id(prod_id, df_all):
    
    df_prod = df_all[df_all.prod_id == prod_id].drop(['prod_id'], axis = 1).unstack()

    df_prod_dict = {}
    for x in df_prod.columns.get_level_values(0).unique():
        if x == 'contract_kind':
            df_prod_dict['main_mask'] = df_prod['contract_kind'] == 'main'
            df_prod_dict['second_main_mask'] = df_prod['contract_kind'] == 'second_main'
        else:
            if x.lower() != 'flag':
                df_prod_dict[x] = df_prod[x]
    
    
    
    save_pickle(df_prod_dict, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/INSAMPLE_%sm/%s.pkl' % (str(bar),prod_id))
    print(prod_id)
    del df_prod_dict

if __name__ == '__main__':
    
    for num, cat in enumerate(sorted(os.listdir('E:warehouse/prod/MD/CHINA_COMMODITY/TICK/MAIN/'))):
        try:
            path_list = glob.glob('E:warehouse/prod/MD/CHINA_COMMODITY/TICK/MAIN/%s/*.csv'%cat)
            if bar != 1:
                path_list = [item for item in path_list if ('2017' in item) or ('2018' in item) or ('2019' in item) or ('2020' in item) or ('2021' in item) or ('2022' in item) or ('2023' in item) or ('2024' in item)]
            else:
                path_list = [item for item in path_list if ('2017' in item) or ('2018' in item) or ('2019' in item) or ('2020' in item) or ('2021' in item) or ('2022' in item) or ('2023' in item) or ('2024' in item)]
            
            path_list = [item for item in path_list if ('20170103' not in item)]
            
            if num == 0:
                print(get_minute_data(path_list[0]))
            
            
            with Pool(28) as pool:
                rlist = pool.map(get_minute_data, path_list)
            
            df_main = pd.concat(rlist).sort_index()
            print('main ends')
            
            df_main['flag'] = df_main[['open','high','low','close','twap']].min(axis = 1)
            
            df_main = df_main[df_main.flag != 0].drop(['flag'], axis = 1)
            
            df_main = df_main.reset_index().drop_duplicates(subset = ['dt','Ticker'], keep = 'first').set_index(['dt','Ticker'])
            
            #try:
            #    IO.pd_hdf5_writer(df_main, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/MAIN_CHINA_COMMODITY_MINUTE.h5'%str(bar), dataset='MAIN_CHINA_COMMODITY_MINUTE', data_columns=['dt','Ticker'], override = True)
            #except:
            #    IO.pd_hdf5_writer(df_main, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/MAIN_CHINA_COMMODITY_MINUTE.h5'%str(bar), dataset='MAIN_CHINA_COMMODITY_MINUTE', data_columns=['dt','Ticker'])
                
            
            path_list = glob.glob('E:warehouse/prod/MD/CHINA_COMMODITY/TICK/SECONDMAIN/%s/*.csv'%cat)
            if bar != 1:
                path_list = [item for item in path_list if ('2017' in item) or ('2018' in item) or ('2019' in item) or ('2020' in item) or ('2021' in item) or ('2022' in item) or ('2023' in item) or ('2024' in item)]
            else:
                path_list = [item for item in path_list if ('2017' in item) or ('2018' in item) or ('2019' in item) or ('2020' in item) or ('2021' in item) or ('2022' in item) or ('2023' in item) or ('2024' in item)]
            path_list = [item for item in path_list if ('20170103' not in item)]
            
            #rlist = Parallel(n_jobs = 20)(delayed(get_minute_data)(i) for i in path_list)
            with Pool(28) as pool:
                rlist = pool.map(get_minute_data, path_list)
            
            df_secondmain = pd.concat(rlist).sort_index()
            print('second_main ends')
            
            
            df_secondmain['flag'] = df_secondmain[['open','high','low','close','twap']].min(axis = 1)
            
            df_secondmain = df_secondmain[df_secondmain.flag != 0]
            
            
            df_secondmain = df_secondmain.reset_index().drop_duplicates(subset = ['dt','Ticker'], keep = 'first').set_index(['dt','Ticker'])
            
            #try:
            #    IO.pd_hdf5_writer(df_secondmain, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/SECONDMAIN_CHINA_COMMODITY_MINUTE.h5'%str(bar), dataset='SECONDMAIN_CHINA_COMMODITY_MINUTE', data_columns=['dt','Ticker'], override = True)
            #except:
            #    IO.pd_hdf5_writer(df_secondmain, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/SECONDMAIN_CHINA_COMMODITY_MINUTE.h5'%str(bar), dataset='SECONDMAIN_CHINA_COMMODITY_MINUTE', data_columns=['dt','Ticker'])
            #print('second_main ends')
            
            
            df_main['contract_kind'] = 'main'
            df_secondmain['contract_kind'] = 'second_main'
            df_secondmain = df_secondmain.reindex(list(set(df_main.index).intersection(set(df_secondmain.index))))
            df_all = pd.concat([df_main.reset_index(), df_secondmain.reset_index()]).rename(columns = {'Ticker':'prod_id','HTSCSecurityID':'Ticker'}).set_index(['dt','Ticker']).sort_index()
            
            try:
                IO.pd_hdf5_writer(df_all, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/%s.h5'%(str(bar), cat), dataset=cat, data_columns=['dt','Ticker'])
            except:
                IO.pd_hdf5_writer(df_all, 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/%s.h5'%(str(bar), cat), dataset=cat, data_columns=['dt','Ticker'], override = True)
            
        except:
            print(cat, '#################################################')
        
        '''
        # 以下为整理成研究环境格式
        print('research format starts')
        df_all = IO.read_data([20170101,20240201],alt= 'E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/h5_%sm/MD_CHINA_COMMODITY_MINUTE.h5'%str(bar))
        df_all['tday'] = df_all['tday'].astype(int)
        prod_id_list = df_all.prod_id.unique().tolist()
        try:
            os.makedirs('E:warehouse/prod/MD/CHINA_COMMODITY/MINUTE/INSAMPLE_%sm/'%(str(bar)))
        except:
            pass
        
        #with Pool(3) as pool:
        #    pool.map(handel_prod_id, prod_id_list)
        
        for item in prod_id_list:
            handel_prod_id(item, df_all)
        '''