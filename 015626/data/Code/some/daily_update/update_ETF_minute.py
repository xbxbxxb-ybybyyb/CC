# 目前聚合的h5时间戳到1459
from xquant.funddata import FundData
fd = FundData()
import pandas as pd
pd.set_option('max_columns',150)
import os
import datetime
from multifactor.data.utils import *
from multiprocessing import Pool
from tqdm import tqdm
import multifactor.utility.dt as udt

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))
    
rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_FUND/ETF/'

tickerlist = ['510500.SH','159922.SZ','159968.SZ','512500.SH','510300.SH','159919.SZ','510330.SH','510050.SH', '512100.SH']
droplist = ['MDRecordID','KLineType','MDDate','MDTime','SecurityID','HTSCSecurityID','PeriodType']

def get_fund_minute(date):
    print(date)
    for ticker in tickerlist:
        tickerpath = os.path.join(rootpath, ticker)
#        if os.path.exists(os.path.join(tickerpath, str(date)+'.csv')):
#            return
        print(ticker)
        df = fd.get_fund_data(ticker, str(date)+" 093000000", str(date)+" 150000000", 'K_1MIN')
        if len(df) == 0:
            continue
        print('has data')
        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df['Ticker'] = ticker
        df = df.drop(droplist,axis = 1)
        df = df.set_index(['dt','Ticker'])
        if not os.path.exists(tickerpath):
            os.makedirs(tickerpath)
        df.to_csv(os.path.join(tickerpath, str(date)+'.csv'))

_,_,cdate_list = check_update_date(20160101,20220719)
#with Pool(processes = 24) as pool:
#    pool.map(get_fund_minute, cdate_list)
#for x in cdate_list:
#    get_fund_minute(x)

# 以下是将csv聚合成h5
import glob
pathlist = glob.glob('/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_FUND/ETF/*/*.csv')

from multiprocessing import Pool
def getdf_bypath(path):
    a = pd.read_csv(path)
    a = a.rename(columns = {'OpenPx':'open','ClosePx':'close','HighPx':'high','LowPx':'low','TotalVolumeTrade':'volume','TotalValueTrade':'amount','NumTrades':'numtrades'})
    a = a[['dt', 'Ticker', 'open', 'close', 'high', 'low', 'numtrades', 'volume', 'amount']]
    a['dt'] = pd.to_datetime(a['dt'])
    return a.set_index(['dt','Ticker'])
    
dflist = []
with Pool(12) as pool:
    dflist = pool.map(getdf_bypath, pathlist)
    
totaldf = pd.concat(dflist, axis = 0).sort_index()

tickerlist = totaldf.index.get_level_values(1).unique().tolist()        
    
result = pd.DataFrame()
for ticker in tickerlist:
    mdf = totaldf.xs(ticker,level = 1).sort_index()
    t_days_list = udt.get_trading_date_range(str(mdf.index[0].date()).replace('-',''),str(mdf.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:59:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    mdf = index_df.join(mdf, how = 'left')
    for col in ['open','high','low','close']:
        mdf[col] = mdf[col].fillna(method = 'ffill')
    for col in ['volume','amount','numtrades']:
        mdf[col] = mdf[col].fillna(value = 0)

    mdf['Ticker'] = ticker
    mdf = mdf.reset_index().set_index(['dt','Ticker']).sort_index()
    result = result.append(mdf)
result = result.sort_index()

IO.pd_hdf5_writer(result, '/data/user/015626/data/share/MD/CHINA_FUND/MINUTE/MD_CHINA_ETF_MINUTE.h5', dataset='MD_CHINA_ETF_MINUTE')

