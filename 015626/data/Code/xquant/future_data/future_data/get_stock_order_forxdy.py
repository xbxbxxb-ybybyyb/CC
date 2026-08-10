import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
import os
import time
from multifactor.data.utils import *
from multiprocessing import Pool

    
from xquant.marketdata import MarketData
#dfs是hdfs连接，若不传，会创建一个新的连接，在sparkmr中使用需要传入该参数，详见sparkmr的demo


def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))


savepath = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction/'

def get_order_data(para):
    
    stock = para[0]
    date = para[1]
    csvpath = os.path.join(savepath,stock,date+'.csv')
    if os.path.exists(csvpath):
        return
    
    mdp = MarketData()
    df = mdp.get_data_by_date("Transaction", stock, date)
    del(mdp)
    if len(df) == 0:
        return
    df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
    # for Order
#    droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID', 'ReceiveDateTime','MDRecordID','MDReportID','MDStreamID','SecuritySubType',
#               'SecurityIDSource','Symbol','MDLevel','MDChannel','TradingPhaseCode','SwitchStatus','MDRecordType','MDValidType','Contactor','ContactInfo',
#               'ConfirmID']
    droplist = ['MDDate', 'MDTime', 'SecurityType', 'HTSCSecurityID', 'ReceiveDateTime','MDRecordID','MDReportID','MDStreamID','SecuritySubType',
               'SecurityIDSource','Symbol','MDLevel','MDChannel','TradingPhaseCode','SwitchStatus','MDRecordType','MDValidType']
    df = df.drop(droplist, axis = 1)
    print(para)
    df.set_index('dt').to_csv(csvpath)

def getflag(x):
    if x.endswith('SZ'):
        return 1
    else:
        return 0
            
newy = pd.read_hdf('/data/user/012245/warehouse/vars/wyc/DATA_CENTER_20150101_20210310.h5')[['label']].loc['20210224':].reset_index()
newy.columns = ['dt','Ticker','label']
newy['dt'] = newy['dt'].apply(lambda x:str(x)[:10].replace('-',''))
newy = newy[['Ticker','dt']]
paralist = newy.values.tolist()

stocklist = newy.Ticker.unique().tolist()
for s in stocklist:
    if not os.path.exists(os.path.join(savepath, s)):
        os.makedirs(os.path.join(savepath, s))
    
with Pool(2) as pool:
    pool.map(get_order_data, paralist)
    