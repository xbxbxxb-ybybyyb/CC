import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
from xquant.marketdata import MarketData
mdp = MarketData()
import os
import time
from multifactor.data.utils import *
from multiprocessing import Pool

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))
    

def get_index_5s_bydate(date):
    date = str(date)
    print(date)

    droplist = ['MDRecordID', 'MDReportID', 'MDDate', 'MDTime', 'MDStreamID', 'SecurityType', 'SecuritySubType', 'SecurityID', 
                'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus',  'MDRecordType', 
                'HTSCSecurityID', 'MDValidType', 'ReceiveDateTime']
    
    namedict = {'000300.SH':'HS300',
                '000905.SH':'ZZ500',
                '000016.SH':'SH50'}
                            
    root_path = '/data/user/015626/data/share/MD/CHINA_INDEX/5s/'
    
    for key in namedict.keys():
        df = mdp.get_data_by_time_frame("Index", key, date + " 092000000", date + " 151000000")
        if len(df) == 0:
            print(date, key, 'is null ***')
            continue
        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df = df.drop(droplist,axis = 1).set_index('dt')
        df.to_csv(os.path.join(root_path, namedict[key], date + '.csv'))
        
_,_,cdate_list = check_update_date(20200701, 20210119)

#with Pool(4) as pool:
#    pool.map(get_index_5s_bydate, cdate_list)
for date in cdate_list:
    get_index_5s_bydate(date)