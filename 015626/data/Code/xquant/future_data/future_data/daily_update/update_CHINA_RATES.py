# -*- coding: utf-8 -*-
from xquant.thirdpartydata.marketdata import MarketData
from multifactor.data.utils import *

from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
import multifactor.utility.dt as udt
from os import listdir
from os.path import isfile, join
import os

def get_dt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')

def select_dates(data):
    # 将每日的时间戳固定为9:30-15:29
    t_days_list = udt.get_trading_date_range(str(data.index[0].date()).replace('-',''),str(data.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','15:29:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')
    data = index_df.join(data, how = 'left')
    
    data[['open','high','low','close']] = data[['open','high','low','close']].fillna(method = 'ffill')
    data[['volume','amount']] = data[['volume','amount']].fillna(value = 0)
    return data

def to_minute(temp_gc):
    volume = temp_gc['TotalVolumeTrade'].diff().resample('T').sum()
    amount = temp_gc['TotalValueTrade'].diff().resample('T').sum()
    temp_gc = temp_gc.loc[(temp_gc['OpenPx']!=0) & (temp_gc['LastPx']!=0) & (temp_gc['HighPx']!=0) & (temp_gc['LowPx']!=0)]
    high_temp = temp_gc['LastPx'].resample('T').max()
    low_temp = temp_gc['LastPx'].resample('T').min()
    open_temp = temp_gc['LastPx'].resample('T').first()
    close_temp = temp_gc['LastPx'].resample('T').last()
    twap = temp_gc['LastPx'].resample('T').mean()
    Ticker = temp_gc['Ticker'].resample('T').last()
    temp_gc_minute = pd.concat([open_temp, close_temp, high_temp, low_temp, twap, volume, amount, Ticker], axis = 1)
    temp_gc_minute.columns = ['open', 'close','high','low', 'twap','volume','amount', 'Ticker']
    temp_gc_minute = temp_gc_minute.loc[~temp_gc_minute['close'].isna()]
    temp_gc_minute = select_dates(temp_gc_minute)
    return temp_gc_minute

def update_data(date_temp):
    date_temp = str(date_temp)
    ma = MarketData()
    dflist = []
    print(date_temp)
    for key, value in update_dict.items():
        data_temp = ma.getMDSecurityTickDataFrame(value,"%s092500"%date_temp,"%s153000"%date_temp,0)
        data_temp['dt'] = data_temp.apply(lambda x: get_dt(x.MDDate, x.MDTime), axis=1)
        data_temp = data_temp.set_index('dt')
        data_temp = data_temp.loc[:, ['NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'OpenPx', 'HighPx', 'LowPx', 'MaxPx', 'MinPx']]
        data_temp['TradingDay'] = date_temp
        data_temp['Category'] = key
        data_temp['Ticker'] = value
        
        os.makedirs(os.path.join(tick_path,key)) if not os.path.exists(os.path.join(tick_path,key)) else None
        os.makedirs(os.path.join(minute_path,key)) if not os.path.exists(os.path.join(minute_path,key)) else None
        data_temp.to_csv(os.path.join(tick_path ,key, date_temp + '.csv'))#下载tick存起来
        
        minutedf = to_minute(data_temp)#tick聚合为minute数据存起来
        minutedf.to_csv(os.path.join(minute_path, key, date_temp + '.csv'))
        dflist.append(minutedf)
    
    thisdaydf = pd.concat(dflist, axis = 0).reset_index().set_index(['dt','Ticker']).sort_index()
    assert len(thisdaydf) > 0
    IO.pd_hdf5_writer(thisdaydf, h5path, dataset=h5path.split('/')[-1].split('.')[0], append = True)
    
    del(ma)

update_dict = {'GC001.SH':'204001.SH', 'GC007.SH':'204007.SH'}

tick_path = '/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_RATES/TICK/'
minute_path = '/arch0/group/800466/warehouse/prod/LOCAL_DATA/CSV/CHINA_RATES/MINUTE/'
h5path = '/data/group/800466/warehouse/prod/MD/CHINA_RATES/MINUTE/CHINA_RATES_MINUTE.h5'

sdate,edate,cdate_list = check_update_date()
flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(edate) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_success = flag_root + str(edate) + '_' + 'china_rates.start'
with open(flag_path_success,'w') as file:
    pass
    
for date in cdate_list:
    update_data(date)
    
flag_path_success = flag_root + str(edate) + '_' + 'china_rates.success'
with open(flag_path_success,'w') as file:
    pass