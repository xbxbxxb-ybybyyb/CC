import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
from xquant.thirdpartydata.marketdata import MarketData
import os
import time
from multifactor.data.utils import *
from multiprocessing import Pool

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))
    
adf = IO.read_data([20200515,20200602], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
#adf['weightsum'] = adf.sum(axis = 1)
adf = adf[adf.index_weight_zz500 > 0]
stock_list = adf.reset_index().Ticker.unique().tolist()

root_path = '/data/user/015626/data/share/MD/CHINA_STOCK/TICK/'
for stock in stock_list:
    save_path = os.path.join(root_path, stock)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
def get_stock_tick_bydate(date):
    date = str(date)
    print(date)
    
    tma = MarketData()

    droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID', 'ReceiveDateTime']
    
                      
    for stock in stock_list:
        df = tma.getMDSecurityTickDataFrame(stock,date + "090000",date + "151000",1)
        if len(df) == 0:
            print(date, stock, 'is null ***')
            continue
        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df = df.drop(droplist,axis = 1).set_index('dt')
    
        df.to_csv(os.path.join(root_path, stock, date + '.csv'))
        
    del(tma)
        
_,_,cdate_list = check_update_date(20200515, 20200602)

with Pool() as pool:
    pool.map(get_stock_tick_bydate, cdate_list)