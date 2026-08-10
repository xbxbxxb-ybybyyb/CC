import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
from xquant.marketdata import MarketData
import os
import time
from multifactor.data.utils import *
from multiprocessing import Pool

def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))

root_path = '/data/user/015626/data/share/MD/CHINA_STOCK/CFG_TICK/'
               
  
def get_stock_tick_bydate(date):
    print(date)
    path = os.path.join(root_path, str(date))
    if not os.path.exists(path):
        os.makedirs(path)
            
    adf = IO.read_data([date, date], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    adf = adf[adf.index_weight_hs300 > 0]
    stock_list = adf.reset_index().Ticker.unique().tolist()
   
    date = str(date)
    
    mdp = MarketData()
    for stock in stock_list:
        df = mdp.get_data_by_date("Stock", stock, date, ["3"], sort_by_receive_time=True)
        if len(df) == 0:
            print(date, stock, 'is null ***')
            continue
        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df['Ticker'] = stock
        droplist = ['MDDate', 'MDTime', 'MDRecordID','MDReportID','MDStreamID' , 'SecurityType', 'SecuritySubType', 
                    'SecurityIDSource','Symbol','MDLevel','MDChannel','TradingPhaseCode','SwitchStatus', 'HTSCSecurityID', 'ReceiveDateTime',
                    'MDRecordType','WithdrawBuyNumber','WithdrawBuyAmount','WithdrawBuyMoney','WithdrawSellNumber','WithdrawSellAmount','WithdrawSellMoney',
                    'TotalBidNumber','TotalOfferNumber','BidTradeMaxDuration','OfferTradeMaxDuration','NumBidOrders','SLYOne','SLYTwo','NorminalPx',
                    'ShortSellSharesTraded','ShortSellTurnover','ReferencePx','ComplexEventStartTime','MDValidType']
        df = df.drop(droplist,axis = 1).set_index(['dt','Ticker'])
        
        df.to_csv(os.path.join(path, stock + '.csv'))
    del(mdp)
        
#get_stock_tick_bydate(20150115)      
_,_,cdate_list = check_update_date(20191030, 20201001)

with Pool(processes = 24) as pool:
    pool.map(get_stock_tick_bydate, cdate_list)
