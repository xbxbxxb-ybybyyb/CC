import sys
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')
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
from multiprocessing import Process


def getdt(a, b):
    strdate = a + ' ' + b
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))


def get_futuretick_bydate(sdate=None, edate=None, kind='MAIN'):
    _, _, cdate_list = check_update_date(sdate, edate)
    droplist_CFE = ['MDDate', 'MDTime', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TotalBidNumber', 'TotalOfferNumber',
                     'SecurityType']

    droplist = ['MDDate', 'MDTime', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TotalBidNumber', 'TotalOfferNumber',
                 'SecurityType', 'Buy2Price', 'Buy2OrderQty', 'Sell2Price', 'Sell2OrderQty',
                'Buy3Price', 'Buy3OrderQty',
                'Sell3Price', 'Sell3OrderQty', 'Buy4Price', 'Buy4OrderQty', 'Sell4Price', 'Sell4OrderQty', 'Buy5Price',
                'Buy5OrderQty',
                'Sell5Price', 'Sell5OrderQty']

    root_path = '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/TICK/' + kind
    for i in range(len(cdate_list)):
        starttime = time.time()
        if i == 0:
            continue
        wind_code_list = IO.read_data([cdate_list[i]],
                                      alt='/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_%s_CHINA_COMMODITY_DAILY.h5' % kind).wind_code.tolist()
        for ticker in wind_code_list:
            try:
                exchange = ticker.split('.')[1]
                contract = ticker.split('.')[0]
                category = ''.join(re.findall(r'[A-Za-z]', contract))
                csvpath = os.path.join(root_path, category + '.' + exchange)

                maticker = ticker
                if exchange == 'CZC':
                    maticker = maticker.replace('CZC', 'ZCE')
                if exchange == 'CFE':
                    maticker = maticker.replace('CFE', 'CF')

                today = str(cdate_list[i])
                yesterday = str(cdate_list[i - 1])

                print(today, ' ', maticker)
                
                if os.path.exists(os.path.join(csvpath, today + '.csv')):
                    continue

                today_d = datetime.datetime.strptime(today, '%Y%m%d')
                yesterday_d = datetime.datetime.strptime(yesterday, '%Y%m%d')
                delta = today_d - yesterday_d
                flag = True
                while (flag):
                    try:
                        if delta > datetime.timedelta(1):
                            yesterday1 = yesterday
                            yesterday2 = str((yesterday_d + datetime.timedelta(1)).strftime('%Y%m%d'))
                            today2 = today
                            today1 = str((today_d - datetime.timedelta(1)).strftime('%Y%m%d'))
                            df_yesterday = ma.getMDSecurityTickDataFrame(maticker, yesterday1 + "20550000",
                                                                         yesterday2 + "20550000", 1)
                            df_today = ma.getMDSecurityTickDataFrame(maticker, today1 + "20550000", today2 + "20550000", 1)
                            df = df_yesterday.append(df_today)
                        else:
                            df = ma.getMDSecurityTickDataFrame(maticker, yesterday + "20550000", today + "20550000", 1)
                        flag = False
                    except Exception as e:
                        print(e)

                if len(df) == 0:
                    print(today, ' ', maticker, '******')
                    file = os.path.join(root_path, kind + str(sdate) + '_' + str(edate) + '.txt')
                    with open(file, 'a+') as f:
                        f.write(today + ' ' + ticker + '\r\n')
                    continue

                df['dt'] = df.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
                if exchange == 'CFE':
                    df = df.drop(droplist_CFE, axis=1).set_index(['dt'])
                else:
                    df = df.drop(droplist, axis=1).set_index(['dt'])
                if not os.path.exists(csvpath):
                    os.makedirs(csvpath)
                df['TradingDate'] = today
                df.to_csv(os.path.join(csvpath, today + '.csv'))
            except Exception as e:
                print(e)
        print(today, time.time() - starttime)


#a, b, c = check_update_date(20210101, None)
#d = int(str(datetime.datetime.strptime(str(a), '%Y%m%d') - datetime.timedelta(days=15)).replace('-', '')[:8])
# _, _, clist = check_update_date(d, a)
# get_futuretick_bydate(clist[-2], clist[-1], kind='MAIN')
#get_futuretick_bydate(20150101, 20220908, kind='MAIN')
if __name__ == '__main__':
    handlers = list()
    date_list = [20200701,20201001,20210101,20210401,20210701,20211001,20220101,20220401,20220701,20220905]
    for i in range(1, len(date_list)):
        handlers.append(Process(target=get_futuretick_bydate, args = (date_list[i-1],date_list[i],'MAIN')))
        handlers.append(Process(target=get_futuretick_bydate, args = (date_list[i-1],date_list[i],'SECONDMAIN')))
    [p.start() for p in handlers]
    [p.join() for p in handlers]