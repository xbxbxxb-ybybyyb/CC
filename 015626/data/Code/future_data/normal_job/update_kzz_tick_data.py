import json
from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import pickle
import numpy as np
from multifactor.data.utils import *

from xquant.bonddata import BondData

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
droplist = ['SecurityID','MDDate', 'MDTime', 'MDRecordID','MDReportID','MDStreamID' , 'SecurityType', 'SecuritySubType', 
                    'SecurityIDSource','Symbol','MDLevel','MDChannel','TradingPhaseCode','SwitchStatus', 'HTSCSecurityID', 'ReceiveDateTime',
                    'MDRecordType','WithdrawBuyNumber','WithdrawBuyAmount','WithdrawBuyMoney','WithdrawSellNumber','WithdrawSellAmount','WithdrawSellMoney',
                    'TotalBidNumber','TotalOfferNumber','BidTradeMaxDuration','OfferTradeMaxDuration','NumBidOrders',
                    'MDValidType']
                    
savepath = '/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/Tick/'
                    
def get_kzz_data_tick(symbol, date):
    spath = os.path.join(savepath,symbol)
    if os.path.exists(os.path.join(spath, str(date) + '.csv')):
        return
    bd = BondData()
    result_min = bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'TICK')
    del(bd)
    if len(result_min) == 0:
#        print(symbol, date, 'no data')
        return
    result_min['dt'] = result_min.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
    result_min = result_min.drop(droplist, axis = 1)
    result_min['Ticker'] = symbol
    result_min = result_min.set_index(['dt','Ticker']).sort_index()
    if not os.path.exists(spath):
        try:
            os.makedirs(spath)
        except:
            pass
    result_min.to_csv(os.path.join(spath, str(date) + '.csv'))

def get_kzz_data_by_date(date):
    print(date)
    bd = BondData()
    kzz_list = bd.get_bond_set(str(date), 'kzz')
    del(bd)
    for symbol in kzz_list:
        get_kzz_data_tick(symbol, date)

sdate,edate,cdate_list = check_update_date(20210619,20210701)

#for x in cdate_list:
#    get_kzz_data_by_date(x)
with Pool(24) as pool:
    pool.map(get_kzz_data_by_date, cdate_list)
