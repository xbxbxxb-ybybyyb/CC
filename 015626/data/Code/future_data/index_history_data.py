from xquant.thirdpartydata.marketdata import MarketData
import pandas as pd
pd.set_option('max_columns', 50)

import matplotlib.pyplot as plt
from multifactor.IO import IO
import os
import datetime
from multifactor.data.utils import *
from multiprocessing import Pool

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))
    


rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/index_history/'
tickerlist = ['000016.SH','000300.SH','000905.SH']
def get_index_data_bydate(date):
    print(date)
    ma = MarketData()
    totaldf = pd.DataFrame()
    for ticker in tickerlist:
        df = ma.getMDSecurityKLineDataFrame(ticker,str(date)+"090000",str(date)+"160000",10,20)
        if len(df) == 0:
            continue
        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df = df[['dt','OpenPx','ClosePx','HighPx','LowPx','TotalVolumeTrade','TotalValueTrade']]
        df['dt'] = pd.to_datetime(df['dt'])
        df['Ticker'] = ticker
        totaldf = totaldf.append(df)
    del(ma)
    if len(totaldf) > 0:
        totaldf = totaldf.set_index(['dt','Ticker'])
        totaldf = totaldf.sort_index()
        totaldf.to_csv(os.path.join(rootpath, str(date) + '.csv'))
        
_, _, cdate_list = check_update_date(20070101, 20140101)
with Pool(processes = 24) as pool:
    pool.map(get_index_data_bydate, cdate_list)