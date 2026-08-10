import os
import pandas as pd
import datetime
from multifactor.IO import IO
import multifactor.utility.dt as udt
import glob
import numpy as np
import warnings
import glob
from multiprocessing import Pool
warnings.filterwarnings('ignore')
import glob

def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(year,month,day,hour,minute,0)

# 将数据变为的每天的标准分钟时间戳 9:30-11:29, 13:00-14:56
def get_standard_index(bdf):
    t_days_list = udt.get_trading_date_range(str(bdf.index[0].date()).replace('-',''),str(bdf.index[-1].date()).replace('-',''))
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
    
    return index_df.join(bdf, how = 'left')

def get_full_minute_stock_data(stock, sdate, edate):
    pklpath = os.path.join(pkl_rootpath, 'UnAdjstedStockMinute_%s.pkl' % stock[:6])
    stk_full_mins_data = pd.read_pickle(pklpath, compression='gzip').reset_index()
    stk_full_mins_data = stk_full_mins_data[(stk_full_mins_data.dt >= sdate) & (stk_full_mins_data.dt <= edate)]
    if len(stk_full_mins_data) == 0:
        return
    stk_full_mins_data = stk_full_mins_data.rename(columns = {'dt':'date'})
    stk_full_mins_data['dt'] = stk_full_mins_data.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
    stk_full_mins_data = stk_full_mins_data.drop(['date','minute','Ticker'], axis = 1)
    stk_full_mins_data = stk_full_mins_data.rename(columns = {'amt':'amount'})
    stk_full_mins_data = stk_full_mins_data.set_index('dt')
#     stk_full_mins_data[['open','high','low','close']] = stk_full_mins_data[['open','high','low','close']].groupby(stk_full_mins_data.index.date).fillna(method = 'ffill')
#     stk_full_mins_data[['volume','amount']] = stk_full_mins_data[['volume','amount']].fillna(value = 0)
    
    stk_full_mins_data = get_standard_index(stk_full_mins_data)
    
    return stk_full_mins_data

ashare_total = IO.read_data([20080710, 21000101],columns = ['CHANGE_DT', 'FLOAT_A_SHR'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareCapitalization/AShareCapitalization.h5')
stkdaily_total = IO.read_data([20120101, 21000101],columns = ['adjfactor'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

def add_turnover_rate_adjfactor(df, stock):
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = ashare_total.xs(stock, level = 1).reset_index()
    ashare = ashare.drop('dt', axis = 1)
    temp = df[['CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT'])
    temp2['FLOAT_A_SHR'] = temp2['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= 20100101]
    temp2 = temp2.drop_duplicates(keep = 'last')

    totaldf = pd.merge(df, temp2, on=['CHANGE_DT'], how = 'left')
    
    dfadj = stkdaily_total.xs(stock, level = 1).reset_index()
    dfadj['CHANGE_DT'] = dfadj.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    dfadj = dfadj.drop(['dt'], axis = 1)
    
    totaldf = pd.merge(totaldf, dfadj, on=['CHANGE_DT'], how = 'left')

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)
    totaldf['turnover_rate'] = totaldf.volume / totaldf.float_shares / 100
    totaldf = totaldf.set_index(['dt'])
    totaldf = totaldf.sort_index()

    return totaldf

def get_xs(df, stock):
    col = df.columns[0]
    try:
        d = df.xs(stock, level = 1)
    except:
        d = pd.DataFrame({col:[]})
        d.index.names = ['dt']
    return d
    
    
stockpath = '/data/group/800002/FutureTrader/test/MD/CHINA_STOCK/MINUTE/'
savepath = '/data/group/800002/FutureTrader/test/MD/CHINA_STOCK/MINUTE_v3/'
linglei_rootpath = '/data/group/800002/FutureTrader/test/data_linglei/MD/CHINA_STOCK/MINUTE/'
pkl_rootpath = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'

stkvol = pd.read_pickle('/data/group/800002/FutureTrader/test/data_linglei/temp/stk_volatility_v2.pkl').loc[pd.to_datetime('20150101'):pd.to_datetime('20210101')]
stkcorr_hs300 = pd.read_pickle('/data/group/800002/FutureTrader/test/data_linglei/temp/stk_index_corr_hs300.pkl').loc[pd.to_datetime('20150101'):pd.to_datetime('20210101')]
stkcorr_zz500 = pd.read_pickle('/data/group/800002/FutureTrader/test/data_linglei/temp/stk_index_corr_zz500.pkl').loc[pd.to_datetime('20150101'):pd.to_datetime('20210101')]

wronglist = []

def get_stock_v2(stock):
    stockdf = IO.read_data([20100101,20210101], alt = os.path.join(stockpath, stock + '.h5'))
    startdate = stockdf.index[0][0].date()
    enddate = stockdf.index[-1][0].date()
    prev_startdate = startdate - datetime.timedelta(days = 31)

    prev_startdate = int(str(prev_startdate).replace('-',''))
    enddate = int(str(enddate).replace('-',''))

    dropdf = stockdf.drop(['open', 'high', 'low', 'close', 'volume', 'amount', 'stk_volatility', 'stk_index_corr_hs300', 'stk_index_corr_zz500', 'float_shares', 'adjfactor', 'turnover_rate'], axis = 1)
    dropdf = dropdf.reset_index(level = 1, drop = True)

    try:
        basedf = get_full_minute_stock_data(stock, prev_startdate, enddate)

        basedf = basedf.join(get_xs(stkvol, stock), how = 'left')
        basedf = basedf.join(get_xs(stkcorr_hs300, stock), how = 'left')
        basedf = basedf.join(get_xs(stkcorr_zz500, stock), how = 'left')

        basedf = add_turnover_rate_adjfactor(basedf, stock)

        basedf = basedf.join(dropdf, how = 'outer')

        basedf['Ticker'] = stock
        basedf = basedf.reset_index().set_index(['dt','Ticker'])

        IO.pd_hdf5_writer(basedf, os.path.join(savepath, stock + '.h5'), dataset=stock)
    except Exception as e:
        print(stock, e)
        wronglist.append((stock, e))
        IO.pd_hdf5_writer(stockdf, os.path.join(savepath, stock + '.h5'), dataset=stock)
        
        
stocklist = [x[:-3] for x in os.listdir(stockpath)]
savelist = [x[:-3] for x in os.listdir(savepath)]
stocklist = list(set(stocklist) - set(savelist))
with Pool(processes=24) as pool:
    pool.map(get_stock_v2, stocklist)