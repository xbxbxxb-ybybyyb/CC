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
    
rootpath = '/data/user/015626/data/share/MD/CHINA_FUND/TICK/510050/'
if not os.path.exists(rootpath):
    os.makedirs(rootpath)
ticker = "510050.SH"
droplist = ['MDRecordID','MDReportID','MDDate','MDTime','MDStreamID', 'SecurityType','SecuritySubType', 'SecurityID','SecurityIDSource','Symbol',
 'MDLevel','MDChannel','TradingPhaseCode', 'SwitchStatus','MDRecordType', 'HTSCSecurityID','ReceiveDateTime', 'MDValidType']

def get_fund_tick(date):
    print(date)

    df = fd.get_fund_data(ticker, str(date)+" 093000000", str(date)+" 150010000", 'TICK')
    df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
    df['Ticker'] = ticker
    df = df.drop(droplist,axis = 1)
    df = df.set_index(['dt','Ticker'])
    df.to_csv(os.path.join(rootpath, str(date)+'.csv'))

_,_,cdate_list = check_update_date(20150101, 20200901)
# with Pool(processes = 24) as pool:
    # pool.map(get_fund_tick, cdate_list)
for x in tqdm(cdate_list):
    try:
        get_fund_tick(x)
    except:
        continue