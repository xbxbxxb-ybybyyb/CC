import sys
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')

from xquant.marketdata import MarketData as XMD

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import multifactor.utility.dt as udt
import numpy as np
import os, glob
from multiprocessing import Pool
import time
from multifactor.data.utils import *
import bottleneck as bk

import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

tick_droplist = ['MDRecordID', 'MDReportID',  'MDStreamID', 'SecurityType', 'SecuritySubType', 'SecurityID',
                             'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus', 'MDRecordType', 
                             'HTSCSecurityID', 'MDValidType', 'NorminalPx', 'ShortSellSharesTraded', 'ShortSellTurnover', 'ReferencePx',
                             'ComplexEventStartTime', 'ComplexEventEndTime']
transaction_droplist = ['MDRecordID', 'MDReportID', 'MDStreamID', 'TradingPhaseCode',
                    'MDValidType',  'SecurityType', 'SecuritySubType', 'SecurityID', 
                    'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'SwitchStatus', 'MDRecordType', 
                    'HTSCSecurityID']
order_droplist = ['MDRecordID', 'MDReportID', 'MDStreamID', 'SecurityType', 'SecuritySubType', 'SecurityID',
          'SecurityIDSource', 'Symbol', 'MDLevel', 'MDChannel', 'TradingPhaseCode', 'SwitchStatus', 'MDRecordType', 
          'HTSCSecurityID', 'MDValidType', 'ExpirationType', 'ExpirationDays', 'Contactor', 'ContactInfo', 'ConfirmID']

def get_auction_data(stock):
    try:
        mdp = XMD()
#        tick = mdp.get_data_by_time_frame("Stock", stock, f"{date} 091500000", f"{date} 092999999")
        transaction = mdp.get_data_by_time_frame("Transaction", stock, f"{date} 091500000", f"{date} 092999999")
#        order = mdp.get_data_by_time_frame("Order", stock, f"{date} 091500000", f"{date} 092999999")
        del(mdp)
#        tick = tick.drop(tick_droplist, axis = 1)
        transaction = transaction.drop(transaction_droplist, axis = 1)
#        order = order.drop(order_droplist, axis = 1)
#        return {stock:[tick, transaction, order]}
        return {stock:[None, transaction, None]}
    except Exception as e:
        return

out_path = '/arch1/group/800466/warehouse/prod/MD/CHINA_STOCK/auction/'
iw = IO.read_data([20180101,20230101], columns = ['index_weight_hs300','index_weight_zz500','index_weight_zz1000'], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
iw = iw.sum(axis = 1)
iw = iw[iw > 0]

_,_,date_list = check_update_date(20190101, 20221109)
for date in date_list:
    print(date)
    pre_date = udt.get_trading_day_offset(str(date),-1)[0].strftime('%Y%m%d')
    stk_list = iw.loc[pre_date].index.get_level_values(1).tolist()

    with Pool(24) as pool:
        rlist = pool.map(get_auction_data, stk_list)

    tick_dict = {}
    transaction_dict = {}
    order_dict = {}
    for x_dict in rlist:
        if x_dict is None:
            continue
        for k,v in x_dict.items():
#            tick_dict[k] = v[0]
            transaction_dict[k] = v[1]
#            order_dict[k] = v[2]

#    save_pickle(tick_dict, os.path.join(out_path, 'Tick', f'{date}.pkl'))
    save_pickle(transaction_dict, os.path.join(out_path, 'Transaction', f'{date}.pkl'))
#    save_pickle(order_dict, os.path.join(out_path, 'Order', f'{date}.pkl'))