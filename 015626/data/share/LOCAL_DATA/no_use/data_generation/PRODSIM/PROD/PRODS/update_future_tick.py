from xquant.futuredata import FutureData
from xquant.compute.aimr import AIMR

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
import datetime
import multifactor.utility.dt as udt

def getdt(a, b):
    strdate = a + ' ' + b
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))


def get_futuretick_bydate(sdate=None, edate=None):
    _, _, cdate_list = check_update_date(sdate, edate)
    droplist_CFE = ['MDDate', 'MDTime', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TotalBidNumber', 'TotalOfferNumber',
                    'HTSCSecurityID', 'SecurityType']

    droplist = ['MDDate', 'MDTime', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TotalBidNumber', 'TotalOfferNumber',
                'HTSCSecurityID', 'SecurityType', 'Buy2Price', 'Buy2OrderQty', 'Sell2Price', 'Sell2OrderQty',
                'Buy3Price', 'Buy3OrderQty',
                'Sell3Price', 'Sell3OrderQty', 'Buy4Price', 'Buy4OrderQty', 'Sell4Price', 'Sell4OrderQty', 'Buy5Price',
                'Buy5OrderQty',
                'Sell5Price', 'Sell5OrderQty']


    ic_list2 = []
    if_list2 = []
    ih_list2 = []
    t_list2 = []

    for year in range(16, 32):
        ic_list2 = ic_list2 + ['IC' + str(a) + '.CFE' for a in range(int('%s01'%year), int('%s13'%year))]
        if_list2 = if_list2 +['IF' + str(a) + '.CFE' for a in range(int('%s01'%year), int('%s13'%year))]
        ih_list2 = ih_list2 +['IH' + str(a) + '.CFE' for a in range(int('%s01'%year), int('%s13'%year))] 
        t_list2 = t_list2 + ['T' + str(a) + '.CFE' for a in range(int('%s01'%year), int('%s13'%year))]
    
    
    #ic_list2 = ['IC' + str(a) + '.CFE' for a in range(1601, 1613)] + ['IC' + str(a) + '.CFE' for a in range(1701, 1713)] + ['IC' + str(a) + '.CFE' for a in range(1701, 1713)] + ['IC' + str(a) + '.CFE' for a in range(1801, 1813)] + ['IC' + str(a) + '.CFE' for a in range(1901, 1913)] + ['IC' + str(a) + '.CFE' for a in range(2001, 2013)] + ['IC' + str(a) + '.CFE' for a in range(2101, 2113)] + ['IC' + str(a) + '.CFE' for a in range(2201, 2213)] + ['IC' + str(a) + '.CFE' for a in range(2301, 2313)]
    #if_list2 = ['IF' + str(a) + '.CFE' for a in range(1601, 1613)] + ['IF' + str(a) + '.CFE' for a in range(1701, 1713)] + ['IF' + str(a) + '.CFE' for a in range(1701, 1713)] + ['IF' + str(a) + '.CFE' for a in range(1801, 1813)] + ['IF' + str(a) + '.CFE' for a in range(1901, 1913)] + ['IF' + str(a) + '.CFE' for a in range(2001, 2013)] + ['IF' + str(a) + '.CFE' for a in range(2101, 2113)] + ['IF' + str(a) + '.CFE' for a in range(2201, 2213)] + ['IF' + str(a) + '.CFE' for a in range(2301, 2313)]
    #ih_list2 = ['IH' + str(a) + '.CFE' for a in range(1601, 1613)] + ['IH' + str(a) + '.CFE' for a in range(1701, 1713)] + ['IH' + str(a) + '.CFE' for a in range(1701, 1713)] + ['IH' + str(a) + '.CFE' for a in range(1801, 1813)] + ['IH' + str(a) + '.CFE' for a in range(1901, 1913)] + ['IH' + str(a) + '.CFE' for a in range(2001, 2013)] + ['IH' + str(a) + '.CFE' for a in range(2101, 2113)] + ['IH' + str(a) + '.CFE' for a in range(2201, 2213)] + ['IH' + str(a) + '.CFE' for a in range(2301, 2313)]
    #t_list2 = ['T' + str(a) + '.CFE' for a in range(1601, 1613)] + ['T' + str(a) + '.CFE' for a in range(1701, 1713)] + ['T' + str(a) + '.CFE' for a in range(1701, 1713)] + ['T' + str(a) + '.CFE' for a in range(1801, 1813)] + ['T' + str(a) + '.CFE' for a in range(1901, 1913)] + ['T' + str(a) + '.CFE' for a in range(2001, 2013)] + ['T' + str(a) + '.CFE' for a in range(2101, 2113)] + ['T' + str(a) + '.CFE' for a in range(2201, 2213)] + ['T' + str(a) + '.CFE' for a in range(2301, 2313)]

    wind_code_list = ic_list2 + if_list2 + ih_list2 + t_list2
    #root_path = '/arch1/group/800466/MarketData/LOCAL_DATA/CSV/TICK/CHINA_FUTURES/ALL_CONTRACT'
    root_path = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/CSV/TICK/CHINA_FUTURES/ALL_CONTRACT'
    for i in range(len(cdate_list)):
        starttime = time.time()
        # if i == 0:
        #     continue
        # wind_code_list = ['IF1806.CFE','IF1809.CFE']
        # wind_code_list = IO.read_data([cdate_list[i]], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/' + kind + '/MD_CHINA_FUTURES_DAILY_' + kind + '.h5').WIND_CODE.tolist()
        for ticker in wind_code_list:

            exchange = ticker.split('.')[1]
            contract = ticker.split('.')[0]
            category = ''.join(re.findall(r'[A-Za-z]', contract))
            csvpath = os.path.join(root_path, contract)

            maticker = ticker
            if exchange == 'CZC':
                maticker = maticker.replace('CZC', 'ZCE')
            if exchange == 'CFE':
                maticker = maticker.replace('CFE', 'CF')

            today = str(cdate_list[i])
            #yesterday = str(cdate_list[i - 1])
            yesterday = str(udt.get_trading_day_offset(int(today), -1)[0].strftime('%Y%m%d'))

            print(today, ' ', maticker)

            today_d = datetime.datetime.strptime(today, '%Y%m%d')
            yesterday_d = datetime.datetime.strptime(yesterday, '%Y%m%d')
            delta = today_d - yesterday_d
            if delta > datetime.timedelta(1):
                yesterday1 = yesterday
                yesterday2 = str((yesterday_d + datetime.timedelta(1)).strftime('%Y%m%d'))
                today2 = today
                today1 = str((today_d - datetime.timedelta(1)).strftime('%Y%m%d'))
                df_yesterday = ma.getMDSecurityTickDataFrame(maticker, yesterday1 + "20550000", yesterday2 + "20550000",
                                                             1)
                df_today = ma.getMDSecurityTickDataFrame(maticker, today1 + "20550000", today2 + "20550000", 1)
                df = df_yesterday.append(df_today)
            else:
                df = ma.getMDSecurityTickDataFrame(maticker, yesterday + "20550000", today + "20550000", 1)

            if len(df) == 0:
                # print(today,' ' ,maticker, '******')
                # file = os.path.join(root_path, kind + str(sdate) + '_' + str(edate) + '.txt')
                # with open(file, 'a+') as f:
                # f.write(today+' '+ticker+'\r\n')
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
        print(today, time.time() - starttime)
        

if __name__ == '__main__':

    #args = AIMR.getParam().split(',')

    #start_date, end_date = '20210921', '21210922'
    a, b, c = check_update_date()

    #a, b, c = check_update_date()
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

    end_date = b
    
    flag_root = flag_rootpath + str(end_date) + '/'

    
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)

    flag_path_start = flag_root + str(end_date) + '_' + 'future_tick.start'
    with open(flag_path_start,'w') as file:
        pass

    get_futuretick_bydate(c[0], c[-1])


    if not os.path.exists(flag_root):
        os.makedirs(flag_root)

    flag_path_success = flag_root + str(end_date) + '_' + 'future_tick.success'
    with open(flag_path_success,'w') as file:
        pass