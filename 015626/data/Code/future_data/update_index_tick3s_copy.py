from xquant.thirdpartydata.marketdata import MarketData
import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
import os
import time
from multifactor.data.utils import *
from multiprocessing import Pool

starttime = 20180101
endtime = 20200602

_,_,cdate_list = check_update_date(starttime, endtime)

root_path = '/data/user/015626/data/share/MD/CHINA_INDEX/TICK/ZZ500'
if not os.path.exists(root_path):
    os.makedirs(root_path)
file = os.path.join(root_path, str(starttime) + '_' + str(endtime) + 'wrong.txt')

weightdf = IO.read_data([starttime, endtime], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
weightdf = weightdf[weightdf.index_weight_zz500 > 0]

indexdf = IO.read_data([starttime, endtime], alt = '/data/group/800080/warehouse/prod/MD/CHINA_INDEX/DAILY/WIND/MD_CHINA_INDEX_DAILY_WIND.h5').xs('000905.SH', level = 1)

# change time from dataframe downloaded
def getdt(a,b):
    strdate = a + ' ' + b 
    x = datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S')
    return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    
# get standard timestamp everyday
def get_dtdf(date):
    
    year = date // 10000
    month = (date % 10000) // 100
    day = date % 100
    timelist = []
    for i in [9, 13]:
        thistime = datetime.datetime(year,month,day,i,30,0) if i == 9 else datetime.datetime(year,month,day,i,0,0)
        timelist.append(thistime)
        for i in range(2 * 60 * 20):
            thistime = thistime + datetime.timedelta(seconds = 3)
            timelist.append(thistime)
    return pd.DataFrame({'dt': timelist})

def get_str_date(date):
    adate = str(date)
    return adate[:4] + '-' + adate[4:6] + '-' + adate[6:]

# get weight dict for every stock
def get_stock_weight(date, adf = weightdf):
    weightdict = adf.xs(get_str_date(date), level = 0)['index_weight_zz500'].to_dict()
    return weightdict
        
def get_index_tick(date):

    stock_start_time = datetime.datetime.now()

    index_preclose = indexdf.loc[get_str_date(date)]['pre_close']

    print(date)
    tma = MarketData()
    
    dtdf = get_dtdf(date)
    weightdict = get_stock_weight(date)
    
    indexdf = dtdf.copy()
    indexdf['LastPx'] = index_preclose
    indexdf['Buy1Price'] = index_preclose
    indexdf['Buy1Amount'] = 0
    indexdf['Sell1Price'] = index_preclose
    indexdf['Sell1Amount'] = 0
    indexdf = indexdf.set_index('dt')
    
    for stock in weightdict.keys(): 

        weight = round(weightdict[stock], 5)
        df = tma.getMDSecurityTickDataFrame(stock, str(date) + "092900", str(date) + "150000", 1)
        
        if len(df) == 0:
            print(str(date) + ' ' + stock + ' no data ******')
            with open(file, 'a+') as f:
                f.write(str(date) + ' ' + stock + ' no data \r\n')
            continue
            
        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        
        df.loc[(df.Sell1Price == 0) & (df.Buy1Price != 0), 'Sell1Price'] = df.PreClosePx * 1.1
        df.loc[(df.Buy1Price == 0) & (df.Sell1Price != 0), 'Buy1Price'] = df.PreClosePx * 0.9
        
        mergedf = pd.merge(dtdf,df,how = 'outer')
        mergedf = mergedf.sort_values('dt')
        mergedf = mergedf.fillna(method = 'ffill')
        
        standarddf = pd.merge(dtdf, mergedf, how = 'left')[['dt', 'PreClosePx', 'LastPx' 'Buy1Price', 'Buy1OrderQty', 'Sell1Price', 'Sell1OrderQty']]
        standarddf['Buy1Amount'] = standarddf['Buy1Price'] * standarddf['Buy1OrderQty']
        standarddf['Sell1Amount'] = standarddf['Sell1Price'] * standarddf['Sell1OrderQty']
        standarddf['Buy1Price'] = (standarddf['Buy1Price'] / standarddf['PreClosePx'] - 1) * weight * index_preclose
        standarddf['Sell1Price'] = (standarddf['Sell1Price'] / standarddf['PreClosePx'] - 1) * weight * index_preclose
        standarddf['LastPx'] = (standarddf['LastPx'] / standarddf['PreClosePx'] - 1) * weight * index_preclose
        standarddf = standarddf[['dt', 'LastPx', 'Buy1Price', 'Buy1Amount', 'Sell1Price', 'Sell1Amount']]
        standarddf = standarddf.set_index('dt')
        
        indexdf = indexdf + standarddf
        
    indexdf.to_csv(os.path.join(root_path, str(date) + '.csv'))
    del(tma)
    
    print(date, datetime.datetime.now() - stock_start_time)
    


with Pool(processes = 24) as pool:
    pool.map(get_index_tick, cdate_list)
        
        