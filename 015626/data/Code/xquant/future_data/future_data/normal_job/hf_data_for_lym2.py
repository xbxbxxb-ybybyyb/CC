import pandas as pd
import numpy as np
import datetime
import re
import os
import warnings
from xquant.marketdata import MarketData as XMD
from xquant.thirdpartydata.marketdata import MarketData as XMDTP
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from multifactor.IO import IO
from tqdm import tqdm
from multiprocessing import Pool
import dill

def format_datetime(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')

def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)

md = IO.read_data([20120101,20230101], columns = ['close'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md = md.reset_index(level = 1)          
def get_stk_list(date):
    return [x for x in md.loc[pd.to_datetime(str(date))].Ticker.tolist() if x[-2:] in ['SZ', 'SH']]
    
def get_level2(ticker):
    mdp = XMD()
#    tick = mdp.get_data_by_date("Stock", ticker, str(date),['1','2','3','5'])
    tick = mdp.get_data_by_time_frame("Stock", ticker, "%s 091500000"%str(date), "%s 093600000"%str(date))
    if len(tick) > 0:
        tick = tick[['MDTime','LastPx','Buy1Price','Sell1Price','TotalBidQty','TotalOfferQty','WeightedAvgBidPx','WeightedAvgOfferPx']]
    # df['dt'] = df.apply(lambda x: format_datetime(x.MDDate, x.MDTime), axis=1)
    # df = df.drop(['MDDate', 'MDTime'], axis = 1).set_index('dt')
#    transaction = mdp.get_data_by_time_frame("Transaction", ticker, "%s 093000000" % date, "%s 093005000" % date)
#    if len(transaction) > 0:
#        transaction = transaction[['MDTime','TradePrice','TradeType']]
#        transaction = transaction[(transaction.TradePrice != 0) & (transaction.TradeType != 1)].drop(['TradeType'], axis = 1)
    del mdp
    return ticker, tick#, transaction
    
_,_,cdate_list1 = check_update_date(20151022,20190101)
cdate_list = cdate_list1 
for date in cdate_list:
    print(date, datetime.datetime.now())
    
    stk_list = get_stk_list(date)
    rlist = []
    with Pool(24) as pool:
        rlist = pool.map(get_level2, stk_list)

    tick_dict = {x[0]:x[1] for x in rlist if len(x[1]) > 0}
#    transaction_dict = {x[0]:x[2] for x in rlist if len(x[2]) > 0}
    diller('/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/special_data_alla/Tick/%s.pkl'%date,tick_dict)
#    diller('/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/special_data_alla/Transaction/%s.pkl'%date,transaction_dict)