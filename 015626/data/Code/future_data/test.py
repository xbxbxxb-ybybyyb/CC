from xquant.funddata import FundData
fd = FundData()
import pandas as pd
pd.set_option('max_columns',150)
import os
import datetime
from multifactor.data.utils import *
from multiprocessing import Pool
from tqdm import tqdm

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))
    
rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/daily/CHINA_FUND/ETF/'

#tickerlist = ['510500.SH','159922.SZ','159968.SZ','512500.SH','510300.SH','159919.SZ','510330.SH','510050.SH']
droplist = ['MDRecordID','KLineType','MDDate','MDTime','SecurityID','HTSCSecurityID','PeriodType']

def get_fund_daily(date):
    print(date)
    tickerlist = fd.get_fund_set(str(date), 'ETF')
    for ticker in tickerlist:
        df = fd.get_fund_data(ticker, str(date)+" 070000000", str(date)+" 230000000", 'K_DAY')
        if len(df) == 0:
            continue
#        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df['dt'] = df['MDDate']
        df['Ticker'] = ticker
        df = df.drop(droplist,axis = 1)
        df = df.set_index(['dt','Ticker'])
        tickerpath = os.path.join(rootpath, ticker)
        if not os.path.exists(tickerpath):
            os.makedirs(tickerpath)
        df.to_csv(os.path.join(tickerpath, str(date)+'.csv'))

_,_,cdate_list = check_update_date(20190618, 20210618)
#with Pool(processes = 8) as pool:
#    pool.map(get_fund_daily, cdate_list)
for x in cdate_list:
    get_fund_daily(x)

#df = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IC_cfg_hf_data_150301_200401.pkl')
#for k in df.keys():
#    df[k].to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/temp/hf_data/%s.pkl' % k)
    
#df = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/IC_cfg_hf_data_150301_200401.pkl')
#for k in df.keys():
#    df[k].to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/INSAMPLE/temp/hf_data/%s.pkl' % k)


'''
weightdf = pd.read_pickle('/data/group/800002/FutureTrader/test/data_linglei/temp/weight.pkl')

v3path = '/data/group/800002/FutureTrader/test/MD/CHINA_STOCK/MINUTE_v3/'
v4path = '/data/group/800002/FutureTrader/test/MD/CHINA_STOCK/MINUTE_v4/'

def add_weight_v4(stock):
    v3df = pd.read_hdf(os.path.join(v3path, stock + '.h5')).drop(['weight'], axis = 1).reset_index(level = 1, drop = True)

    w = weightdf.xs(stock, level = 1)

    df = v3df.join(w, how = 'left')

    df['Ticker'] = stock
    df = df.reset_index().set_index(['dt','Ticker'])

    IO.pd_hdf5_writer(df, os.path.join(v4path, stock + '.h5'), dataset=stock)

stocklist = [x[:-3] for x in os.listdir(v3path)]
with Pool(24) as pool:
    pool.map(add_weight_v4, stocklist)
'''