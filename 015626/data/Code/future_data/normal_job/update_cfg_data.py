from multifactor.IO import IO
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import os
import datetime
from multifactor.data.utils import *
import multifactor.utility.dt as udt

def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(year,month,day,hour,minute,0)
    
def minute_flag_check(date):
    path1 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_' + 'MINUTE.success'
    path2 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_' + 'INDEX_WEIGHT.success'
    return os.path.exists(path1) and os.path.exists(path2)


# update code
for ticker in ['IC.CFE', 'IF.CFE']:

    rootpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
    h5name = 'IC_STOCKS_MINUTE_DATA.h5' if ticker == 'IC.CFE' else 'IF_STOCKS_MINUTE_DATA.h5'
    target_h5path = os.path.join(rootpath, h5name)

    print(ticker, ' read now data')
    nowalldf = IO.read_data([20000101,21000101], alt = target_h5path)
    sdate,_,cdate_list = check_update_date(int(str(nowalldf.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
    startdate = cdate_list[1]
    enddate = cdate_list[-1]
    assert sdate != startdate
    print(ticker, ' read data done, start check minute flag')
    
    while True:
        if minute_flag_check(enddate):
            break
    print('start update data')

    #startdate, enddate = 20200605, 20210101
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
    tickercolumn = tickerdict[ticker]
    namedict = {'IC.CFE':'_zz500','IF.CFE':'_hs300','IH.CFE':'_sh50'}
    columnnamelater = namedict[ticker]
    indexweight = IO.read_data([startdate, enddate], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    zz500df = indexweight[indexweight[tickercolumn] > 0].reset_index()
    zz500df['dt'] = zz500df['dt'].apply(lambda x:int(datetime.datetime.strftime(x,'%Y%m%d')))
    dtlist = zz500df.dt.unique().tolist()



    df = pd.DataFrame()
    for date in dtlist:
        print(ticker, date)
        mdf = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/' + str(date) + '.pkl', compression = 'gzip')
        mdf = mdf.reset_index()
        mdf['Ticker'] = mdf.Ticker.apply(lambda x:ticker_match(x))
        
        tickerlist = zz500df[zz500df.dt == date].Ticker.tolist()
        mdf = mdf[mdf.Ticker.isin(tickerlist)]
        
        mdf = mdf.rename(columns = {'dt':'date'})
        mdf['dt'] = mdf.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
        
        mdf = mdf.drop(['date','minute'], axis = 1)
        df = df.append(mdf)
     
    df = df.sort_values(['dt','Ticker'])   
    df = df.set_index(['dt','Ticker']).sort_index()
    #IO.pd_hdf5_writer(df, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/IF_STOCKS_MINUTES_DATA.h5', dataset='IF')

    # calculate turnover
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = IO.read_data([20080710, 21000101],columns = ['CHANGE_DT', 'FLOAT_A_SHR'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareCapitalization/AShareCapitalization.h5')
    ashare = ashare.reset_index()
    ashare = ashare.drop('dt', axis = 1)
    temp = df[['Ticker','CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['Ticker','CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT','Ticker'])
    temp2['FLOAT_A_SHR'] = temp2.groupby('Ticker')['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= startdate]
    temp2 = temp2[temp2.Ticker.isin(df.Ticker.unique().tolist())]
    temp2 = temp2.drop_duplicates(keep = 'last')

    totaldf = pd.merge(df, temp2, on=['Ticker','CHANGE_DT'], how = 'left')

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)
    totaldf['turnover'] = totaldf.volume / totaldf.float_shares / 100
    totaldf = totaldf.set_index(['dt','Ticker'])
    totaldf = totaldf.sort_index()
    #IO.pd_hdf5_writer(totaldf, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/IF_STOCKS_MINUTES_DATA_turnover.h5', dataset='IF')    
                
    # add weight
    nowdf = totaldf
    pre_startdate = int(str(datetime.datetime.strptime(str(startdate), '%Y%m%d') - datetime.timedelta(days = 30))[:10].replace('-',''))
    indexweight = IO.read_data([pre_startdate, enddate], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    zz500df = indexweight[indexweight[tickercolumn] > 0][[tickercolumn]]
    zz500df = zz500df.unstack().shift(1).stack()
    
    adjdf = IO.read_data([startdate, enddate],columns = ['adjfactor'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    nowdf = nowdf.reset_index().rename(columns = {'dt':'minute'})
    nowdf['dt'] = nowdf.minute.apply(lambda x:x.date())
    nowdf = nowdf.set_index(['dt','Ticker'])

    df = nowdf.join(zz500df, how = 'left').join(adjdf, how = 'left')
    df = df.reset_index()
    df = df.drop('dt', axis = 1)
    df = df.rename(columns = {'minute':'dt',tickercolumn:'weight','amt':'amount'})
    df = df.set_index(['dt','Ticker']).sort_index()
    clist = df.columns.tolist()
    cdict = {x:x + columnnamelater for x in clist}
    df = df.rename(columns = cdict)

    nowalldf = nowalldf.append(df)
    nowalldf = nowalldf.sort_index()
    
    os.remove(target_h5path) if os.path.exists(target_h5path) else None
    IO.pd_hdf5_writer(nowalldf, target_h5path, dataset=ticker[:2])
    print(ticker, ' update done')