from multifactor.IO import IO
import pandas as pd
import os
import datetime
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool
from xquant.xqutils.helper import link

from xquant.compute.aimr import AIMR
import multifactor.utility.dt as udt
from multifactor.data.utils import *
import time

from xquant.marketdata import MarketData
ma = MarketData()

ROOT_PATH = '/data/group/800466/warehouse/prod/MD/MarketData'

def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),0)

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
def standard_index(data):
    t_days_list = udt.get_trading_date_range(str(data.index[0].date()).replace('-',''),str(data.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:56:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    data = index_df.join(data, how = 'left')
    return data
    
def update_index_data(date):
    save_path = '{}/MD/CHINA_INDEX/MINUTE/'.format(ROOT_PATH)
    start_date = str(date) + '090000'
    end_date = str(date) + '153000'

    index_list = ['000016.SH', '000300.SH', '000905.SH', '000852.SH', '000688.SH']
    for ind in index_list:
        print(ind)
        df = ma.get_data_by_date("Kline1M4ZT", ind, str(date))
        df_xquant = df[['MDTime','OpenPx','HighPx','LowPx','ClosePx','TotalVolumeTrade','TotalValueTrade']]
        df_xquant.columns = ['minute','open','high','low','close','volume','amount']
        df_xquant['minute'] = df_xquant['minute'].apply(lambda x : int(x[:4]))
        df_xquant['date'] = int(date)
        df_xquant['dt'] = df_xquant.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
        df_xquant['Ticker'] = ind
        df_xquant = df_xquant.set_index(['dt']).drop(['minute','date'], axis = 1)
        data = standard_index(df_xquant)
        
        df_tick = ma.get_data_by_date("Index", ind, str(date))
        df_tick['dt'] = df_tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        df_tick = df_tick.set_index('dt')
        hopen = (df_tick['LastPx'].resample('1min').first())
        hopen.name = 'open'
        hclose = (df_tick['LastPx'].resample('1min').last())
        hclose.name = 'close'

        hamount = (df_tick['TotalValueTrade'].diff().resample('1min').sum())
        hamount.name = 'amount'

        hvolume = (df_tick['TotalVolumeTrade'].diff().resample('1min').sum())
        hvolume.name = 'volume'
        
        data['volume'] = standard_index(hvolume)
        data['amount'] = standard_index(hamount)
        
        data['open'] = standard_index(hopen)
        data['close'] = standard_index(hclose)
        
        for k in ['close','open','high','low']:
            data[k] = data[k].fillna(method = 'ffill')
        for k in ['volume','amount']:
            data[k] = data[k].fillna(value = 0)
        
        data = data.reset_index().set_index(['dt','Ticker'])
        IO.pd_hdf5_writer(data, os.path.join(save_path, ind + '.h5'), dataset = ind, append = True)

        # return data


if __name__ == '__main__':
    #args = AIMR.getParam().split(',')
    
    #start_date, end_date = '20210922', '20210922'
    sdate,edate,cdate_list = check_update_date()
    flag_rootpath =  '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

    end_date = edate
    
    flag_root = flag_rootpath + str(end_date) + '/'

    
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)

    flag_path_start = flag_root + str(end_date) + '_' + 'INDEX.start'
    with open(flag_path_start,'w') as file:
        pass
    for date in cdate_list:
        update_index_data(date)
    
    _flag = True
    lm = link.LinkMessage()

    for index in ['000016.SH', '000300.SH', '000905.SH', '000852.SH']:
        length = len(pd.read_hdf('/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE/%s.h5'%index).reset_index().set_index('dt').loc[str(date)]['Ticker'].dropna())
        if length < 237:
            lm.sendMessage(index + '___' + str(length))
            _flag = False
        
    if _flag:
        flag_path_success = flag_root + str(end_date) + '_' + 'INDEX.success'
        with open(flag_path_success,'w') as file:
            pass