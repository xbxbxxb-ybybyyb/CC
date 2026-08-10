from multifactor.IO import IO
import pandas as pd
import os
import datetime
from multifactor.data.utils import *
import multifactor.utility.dt as udt

def get_next_day(a):
    year = a // 10000
    month = a % 10000 // 100
    day = a % 100
    return int(str((datetime.datetime(year,month,day) + datetime.timedelta(1)).date()).replace('-',''))
    
def update_by_date(date):
    print(date, ' start update')
    df = IO.read_data([date, get_next_day(date)], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
    df = df.drop(['trading_day','EXCHANGE'], axis = 1)
    df = df.loc[(slice(None),['IC.CFE','IF.CFE','IH.CFE']),:]
    df = df.sort_index()
    assert len(df) > 200
    IO.pd_hdf5_writer(df, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/WIND_MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN_ALL.h5', dataset='mainall', append=True)
    idx = df.index.get_level_values(0)
    t1 = df.loc[(idx.hour == 9) & (idx.minute >= 30)]
    t2 = df.loc[(idx.hour == 10) | (idx.hour == 13)]
    t3 = df.loc[(idx.hour == 11) & (idx.minute < 30)]
    t4 = df.loc[(idx.hour == 14) & (idx.minute <= 57)]
    t = t1.append(t2).append(t3).append(t4)
    t = t.sort_index()
    
    result = pd.DataFrame()
    for ticker in ['IF.CFE','IC.CFE','IH.CFE']:
        mdf = t.xs(ticker,level = 1)
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

        mdf['Ticker'] = ticker
        mdf = mdf.reset_index().set_index(['dt','Ticker']).sort_index()
        result = result.append(mdf)
    result = result.sort_index()
    
    IO.pd_hdf5_writer(result, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/WIND_MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5', dataset='main', append=True)
    
#    for ticker in ['IF.CFE','IH.CFE','IC.CFE']:
#        adf = t.xs(ticker, level = 1)
#        clist = adf.columns.tolist()
#        namedict = {}
#        for c in clist:
#            namedict[c] = c + '_' + str.lower(ticker[:2])
#        adf = adf.rename(columns = namedict)
#        adf['Ticker'] = ticker
#        adf = adf.reset_index().set_index(['dt','Ticker'])
#        IO.pd_hdf5_writer(adf, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_' + ticker[:2] + '_MINUTE_MAIN.h5', dataset=str.lower(ticker[:2]), append = True)
    
    print(date, ' update done')
    
    
_,edate,cdate_list = check_update_date()

def minute_flag_check(date):
    path1 = '/data/user/012245/warehouse/flags/' + str(date) + '/' + str(date) + '_COMMODITY_BASE.success'
    return os.path.exists(path1)

print('------wait doc.Xu flag')
while True:
    if minute_flag_check(edate):
        break
    time.sleep(60)

for date in cdate_list:
    update_by_date(date)
    
# get history data
'''
df = IO.read_data([20100101,20200701], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
finaldf = pd.DataFrame()
for ticker in ['IC.CFE', 'IH.CFE', 'IF.CFE']:
    icdf = df.xs(ticker, level = 1)
    idx = icdf.index
    t1 = icdf.loc[(idx.hour == 9) & (idx.minute >= 30)]
    t2 = icdf.loc[(idx.hour == 10) | (idx.hour == 13)]
    t3 = icdf.loc[(idx.hour == 11) & (idx.minute < 30)]
    t4 = icdf.loc[(idx.hour == 14) & (idx.minute <= 57)]
    t = t1.append(t2).append(t3).append(t4)
    t = t.sort_index()
    t['Ticker'] = ticker
    
    finaldf = finaldf.append(t)
    
finaldf = finaldf.reset_index()
finaldf = finaldf.sort_values(['dt','Ticker'])
finaldf = finaldf.set_index(['dt','Ticker'])
finaldf = finaldf.drop(['trading_day','EXCHANGE'], axis = 1)

IO.pd_hdf5_writer(finaldf, '/data/user/015626/data/share/MD/STOCK_INDEX_FUTURES/MD_CHINA_FUTURES_MINUTE_MAIN.h5', dataset = 'main')
'''