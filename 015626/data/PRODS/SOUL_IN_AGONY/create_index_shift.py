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
from joblib import Parallel, delayed
from xquant.marketdata import MarketData
ma = MarketData()

ss = 10
print(ss)


def switch_time(item, seconds = ss):
    assert len(str(item)) == 9, 'FUCK'
    adjs = seconds * 1000
    
    item_temp = int(item)
    #if (int(item) >= 113000000) and (int(item) < 130000000):
    #    return str(item)

    if (item_temp >= 130000000) and (item_temp < 130000000 + adjs):

        item_temp1 = item_temp - 17000000

    else:
        item_temp1 = item_temp
    if int(str(item_temp1)[-5:]) < adjs:
        if (str(item_temp1)[-7:-5] == '00'):

            item_temp2 = int(item_temp1 - 4040000 - adjs)
        else:
            item_temp2 = int(item_temp1 - 40000 - adjs)
    else:
        item_temp2 = int(item_temp1 - adjs)
    item_final = str(item_temp2)
    if item_final[0] != '1':
        item_final = '0' + item_final
    return item_final

ROOT_PATH = '/dfs/group/800466/warehouse/prod/MD/MarketData'

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
    
def update_index_data(date, ind):
    print(ind)
    start_date = str(date) + '090000'
    end_date = str(date) + '153000'

    df_tick = ma.get_data_by_date("Index", ind, str(date))
    
    df_tick = df_tick[(df_tick['MDTime'].astype(int) < 113000000) | (df_tick['MDTime'].astype(int) >= 130000000)]
    df_tick['MDTime'] = df_tick['MDTime'].apply(lambda x: switch_time(x))
    
    df_tick['dt'] = df_tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
    df_tick = df_tick.set_index('dt')

    hopen = (df_tick['LastPx'].resample('1min').first())
    hopen.name = 'open'
    hclose = (df_tick['LastPx'].resample('1min').last())
    hclose.name = 'close'

    hhigh = (df_tick['LastPx'].resample('1min').max())
    hhigh.name = 'high'

    hlow = (df_tick['LastPx'].resample('1min').min())
    hlow.name = 'low'

    hamount = (df_tick['TotalValueTrade'].diff().resample('1min').sum())
    hamount.name = 'amount'

    hvolume = (df_tick['TotalVolumeTrade'].diff().resample('1min').sum())
    hvolume.name = 'volume'


    data = pd.concat([standard_index(hopen), standard_index(hhigh), standard_index(hlow), standard_index(hclose), standard_index(hamount), standard_index(hvolume)], axis = 1)
    data['Ticker'] = ind
    for k in ['close','open','high','low']:
        data[k] = data[k].fillna(method = 'ffill')
    for k in ['volume','amount']:
        data[k] = data[k].fillna(value = 0)
    data = data.reset_index().set_index(['dt','Ticker'])
    #IO.pd_hdf5_writer(data, os.path.join(save_path, ind + '.h5'), dataset = ind, append = True)

    return data


        

if __name__ == '__main__':
    #args = AIMR.getParam().split(',')
    
    #start_date, end_date = '20210922', '20210922'
    sdate,edate,cdate_list = check_update_date(20190101, 20250316)
    flag_rootpath =  '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

    end_date = edate
    
    flag_root = flag_rootpath + str(end_date) + '/'

    
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    
    save_path = '{}/MD/CHINA_INDEX/MINUTE_shift_30/'.format(ROOT_PATH)
    save_path = save_path.replace('_shift_30', '_shift_%s'%ss)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    print(save_path)
    d50 = Parallel(n_jobs= -1)(delayed(update_index_data)(date, '000016.SH') for date in cdate_list)
    print('50')
    IO.pd_hdf5_writer(pd.concat(d50).sort_index(), os.path.join(save_path, '000016.SH' + '.h5'), dataset = '000016.SH', override = True)
    
    
    d300 = Parallel(n_jobs= -1)(delayed(update_index_data)(date, '000300.SH') for date in cdate_list)
    print('300')
    IO.pd_hdf5_writer(pd.concat(d300).sort_index(), os.path.join(save_path, '000300.SH'+ '.h5'), dataset = '000300.SH', override = True)
    
    
    d500 = Parallel(n_jobs= -1)(delayed(update_index_data)(date, '000905.SH') for date in cdate_list)
    print('500')
    IO.pd_hdf5_writer(pd.concat(d500).sort_index(), os.path.join(save_path, '000905.SH' + '.h5'), dataset = '000905.SH', override = True)


    d1000 = Parallel(n_jobs= -1)(delayed(update_index_data)(date, '000852.SH') for date in cdate_list)
    print('1000')
    IO.pd_hdf5_writer(pd.concat(d1000).sort_index(), os.path.join(save_path, '000852.SH' + '.h5'), dataset = '000852.SH', override = True)