import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
from multifactor.data.utils import *

face_value_dict = {'IC.CFE': 200,
                           'IF.CFE': 300,
                           'IH.CFE': 300}

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:50', freq='10S').to_list() + pd.date_range('13:00:00','14:59:50',freq='10S').to_list()
    t_mins_list = ['09:29:00'] + [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()

def get_10s(para):
    date = para[0]
    tick = pd.read_csv('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/%s/%s.csv' % (para[2][:6],str(date)), index_col=0, parse_dates=True)#.reset_index()
#    tick = tick.sort_values(by = 'dt')
#    tick['seconds_10s'] = tick.dt.map(lambda x: x.replace(microsecond=0))
#    index3s = pd.date_range(str(date)+'090000',str(date)+'150000', freq ='10S').tolist()
#    tick.loc[~tick.seconds_10s.isin(index3s),'seconds_10s'] = np.nan
#    tick['seconds_10s'] = tick['seconds_10s'].fillna(method = 'ffill')

    tick[['volume','amount']] = tick[['TotalVolumeTrade','TotalValueTrade']].diff()
    tick['volume'] = tick['volume'].fillna(tick['TotalVolumeTrade'])
    tick['amount'] = tick['amount'].fillna(tick['TotalValueTrade'])

    tick['open'] = tick['LastPx']
    tick['high'] = tick['LastPx']
    tick['low'] = tick['LastPx']
    tick['close'] = tick['LastPx']
    tick['volume'] = tick['volume']
    tick['amount'] = tick['amount']
    tick['twap'] = tick['LastPx']

    tick['buyv_sum'] = 0
    tick['sellv_sum'] = 0
    for i in range(1,6):
        tick['buyv_sum'] += tick['Buy%sOrderQty' % i]
        tick['sellv_sum'] += tick['Sell%sOrderQty' % i]

    tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
    tick['v_imbalance'] = tick['Buy1OrderQty']/(tick['Buy1OrderQty'] + tick['Sell1OrderQty'])

    tick['OBI_5'] = (tick['buyv_sum'] - tick['sellv_sum']) / (tick['buyv_sum'] + tick['sellv_sum'])
    tick['v_imbalance_5'] = tick['buyv_sum']/(tick['buyv_sum'] + tick['sellv_sum'])

    tick['spread'] = tick['Sell1Price'] - tick['Buy1Price']

    tick.loc[tick['Buy1Price'] < tick['Buy1Price'].shift(), 'VBt'] = 0
    tick.loc[tick['Buy1Price'] == tick['Buy1Price'].shift(), 'VBt'] = tick['Buy1OrderQty'] - tick['Buy1OrderQty'].shift()
    tick.loc[tick['Buy1Price'] > tick['Buy1Price'].shift(), 'VBt'] = tick['Buy1OrderQty']
    tick.loc[tick['Sell1Price'] > tick['Sell1Price'].shift(), 'VAt'] = 0
    tick.loc[tick['Sell1Price'] == tick['Sell1Price'].shift(), 'VAt'] = tick['Sell1OrderQty'] - tick['Sell1OrderQty'].shift()
    tick.loc[tick['Sell1Price'] < tick['Sell1Price'].shift(), 'VAt'] = tick['Sell1OrderQty']
    tick['OIt'] = (tick['VBt'] - tick['VAt'])
    tick['OISt'] = tick['OIt']/(tick['Sell1Price'] - tick['Buy1Price'])
    tick['OIRt'] = (tick['VBt'] - tick['VAt'])/(tick['VBt'] + tick['VAt'])
    condition = (tick['VBt'] + tick['VAt']) == 0
    tick.loc[condition ,'OIRt'] = 0

    aggdict_ohlcva = {'open':'first','high':'max','low':'min','close':'last','volume':'sum','amount':'sum','twap':'mean','OpenInterest':'last','OBI':'mean','OBI_5':'mean','v_imbalance':'mean','v_imbalance_5':'mean',
                     'spread':'mean','VBt':'mean','VAt':'mean','OIt':'mean','OISt':'mean','OIRt':'mean'}
    ohlcva = tick.resample('10S').agg(aggdict_ohlcva)
    ohlcva.index.name = 'dt'

    standard_index = get_index_fromdate(date)

    ohlcva = standard_index.join(ohlcva,how = 'left')
    
    ohlcva['vwap'] = ohlcva['amount'] / ohlcva['volume'] / face_value_dict[para[1]]
    ohlcva = ohlcva.replace([np.inf,-np.inf], np.nan)
    ohlcva['vwap'] = ohlcva['vwap'].replace(0, np.nan)
    ohlcva['twap'] = ohlcva['twap'].replace(0, np.nan)
    ohlcva = ohlcva.rename(columns = {'OpenInterest':'position'})
    
    columns = ohlcva.columns.tolist()
    for k in ['open','high','low','close','twap','vwap','position']:
        if k in columns:
            ohlcva[k] = ohlcva[k].replace(0,np.nan).fillna(method = 'pad')
    res_columns = list(set(columns) - set(['open','high','low','close','twap','vwap','position']))
    for k in res_columns:
        if k in columns:
            ohlcva[k] = ohlcva[k].fillna(0)
            
    ohlcva['twap'] = round(ohlcva['twap'],2)
    ohlcva['vwap'] = round(ohlcva['vwap'],2)
    ohlcva['Ticker'] = para[1]
    ohlcva['contract_00'] = para[2]
    ohlcva = ohlcva.reset_index().set_index(['dt','Ticker'])
    return ohlcva
    
sdate, edate = 20161201, 20220617

univ = IO.read_data([sdate, edate], columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
univ = univ.reset_index()
dtlist = [int(x.strftime('%Y%m%d')) for x in univ.dt.tolist()]
tickerlist = univ.Ticker.tolist()
contractlist = univ.contract_00.tolist()
paralist = []
for i in range(len(dtlist)):
    paralist.append([dtlist[i], tickerlist[i], contractlist[i]])

dflist = []
with Pool(24) as pool:
    dflist = pool.map(get_10s, paralist)

df = pd.concat(dflist, axis = 0).sort_index()

IO.pd_hdf5_writer(df,'/data/user/015626/data/share/MD/CHINA_FUTURES/10s/RECENT_MONTH_FUTURE_10S.h5', dataset='RECENT_MONTH_FUTURE_10S')