from xquant.futuredata import FutureData
fd = FutureData()
import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
from xquant.thirdpartydata.marketdata import MarketData
ma = MarketData()
import os
import time
from multifactor.data.utils import *

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))


def get_futuretick_bydate(sdate = None, edate = None):
    _,_,cdate_list = check_update_date(sdate, edate)
    droplist_CFE = ['MDDate', 'MDTime', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TotalBidNumber', 'TotalOfferNumber', 
            'HTSCSecurityID', 'SecurityType']

    droplist = ['MDDate', 'MDTime', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TotalBidNumber', 'TotalOfferNumber', 
            'HTSCSecurityID', 'SecurityType', 'Buy2Price', 'Buy2OrderQty', 'Sell2Price', 'Sell2OrderQty', 'Buy3Price', 'Buy3OrderQty', 
            'Sell3Price', 'Sell3OrderQty', 'Buy4Price', 'Buy4OrderQty', 'Sell4Price', 'Sell4OrderQty', 'Buy5Price', 'Buy5OrderQty', 
            'Sell5Price', 'Sell5OrderQty']
    
    
    ic_list = ['IC'+str(a)+'.CFE' for a in range(1701,1713)]
    if_list = ['IF'+str(a)+'.CFE' for a in range(1701,1713)]
    ih_list = ['IH'+str(a)+'.CFE' for a in range(1701,1713)]
    wind_code_list = ic_list + if_list + ih_list 
    root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE'
    for i in range(len(cdate_list)):
        starttime = time.time()
        if i == 0:
           continue
        
        # wind_code_list = IO.read_data([cdate_list[i]], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/' + kind + '/MD_CHINA_FUTURES_DAILY_' + kind + '.h5').WIND_CODE.tolist()
        for ticker in wind_code_list:
           
           exchange = ticker.split('.')[1]
           contract = ticker.split('.')[0]
           category = ''.join(re.findall(r'[A-Za-z]', contract))
           csvpath = os.path.join(root_path,contract)
           
           maticker = ticker
           if exchange == 'CZC':
                maticker = maticker.replace('CZC','ZCE')
           if exchange == 'CFE':
                maticker = maticker.replace('CFE','CF')
           
           today = str(cdate_list[i])
           yesterday = str(cdate_list[i - 1])
           
           print(today,' ' ,maticker)
           
           today_d = datetime.datetime.strptime(today,'%Y%m%d')
           yesterday_d = datetime.datetime.strptime(yesterday,'%Y%m%d') 
           delta = today_d - yesterday_d
           if delta > datetime.timedelta(1):
                yesterday1 = yesterday
                yesterday2 = str((yesterday_d + datetime.timedelta(1)).strftime('%Y%m%d'))
                today2 = today
                today1 = str((today_d - datetime.timedelta(1)).strftime('%Y%m%d'))
                try:
                    df_yesterday = ma.getMDSecurityTickDataFrame(maticker, yesterday1+"20550000", yesterday2 + "20550000",1)
                    df_today = ma.getMDSecurityTickDataFrame(maticker, today1+"20550000", today2 + "20550000",1)
                    df = df_yesterday.append(df_today)
                except:
                    print('wrong!!!')
                    continue
           else:
                try:
                    df = ma.getMDSecurityTickDataFrame(maticker, yesterday + "20550000", today + "20550000",1)
                except:
                    print('wrong!!!')
                    continue
                
           if len(df) == 0:
                # print(today,' ' ,maticker, '******')
                # file = os.path.join(root_path, kind + str(sdate) + '_' + str(edate) + '.txt')
                # with open(file, 'a+') as f:
                      # f.write(today+' '+ticker+'\r\n')
                continue
                
           df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
           if exchange == 'CFE':
                df = df.drop(droplist_CFE, axis = 1).set_index(['dt'])
           else:
                df = df.drop(droplist, axis = 1).set_index(['dt'])
           if not os.path.exists(csvpath):
                os.makedirs(csvpath)
           df['TradingDate'] = today
           df.to_csv(os.path.join(csvpath,today+'.csv'))
        print(today, time.time() - starttime)
        
get_futuretick_bydate(20160701, 20180101)