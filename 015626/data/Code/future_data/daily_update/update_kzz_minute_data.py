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
bd = BondData()

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')

def get_kzz_data(symbol, date):
    result_min = bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'K_1MIN')
    if len(result_min) == 0:
#        print(symbol, date, 'no data')
        return
    result_min['dt'] = result_min.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
    result_min = result_min.drop(droplist, axis = 1)
    result_min['Ticker'] = symbol
    result_min = result_min.set_index(['dt','Ticker']).rename(columns = column_name_dict)
    return result_min

def get_kzz_data_by_date(date):
    print(date)
    kzz_list = bd.get_bond_set(str(date), 'kzz')
    result_list = []
    for symbol in kzz_list:
        result_list.append(get_kzz_data(symbol, date))
    if len(result_list) == 0:
        return
    result = pd.concat(result_list, axis = 0).sort_index()
    result.to_pickle(os.path.join(savepath,'%s.pkl'%str(date)), compression = 'gzip')
    return result
    
droplist = ['MDRecordID', 'KLineType', 'SecurityID', 'HTSCSecurityID', 'MDDate',
       'MDTime','PeriodType', 'IOPV', 'OpenInterest', 'SettlePrice']
column_name_dict = {'OpenPx':'open', 'ClosePx':'close', 'HighPx':'high', 'LowPx':'low',  'TotalVolumeTrade':'volume', 'TotalValueTrade':'amount'}

savepath = '/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/MINUTE/per_date/'
sdate,edate,cdate_list = check_update_date()

result_list = []
for x in cdate_list:
    result_list.append(get_kzz_data_by_date(x))
    
append_df = pd.concat(result_list, axis = 0).sort_index()
IO.pd_hdf5_writer(append_df, '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE.h5', dataset = 'CHINA_CONVERTIBLE_BOND_MINUTE', append = True)

# 以上为每日更新可转债分钟数据，以下为基本信息表

a = IO.read_data(columns = ['close'], alt = '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE.h5')

tickerlist = a.index.get_level_values(1).unique().tolist()


infolist = []
for t in tickerlist:
    info = bd.get_bond_issuance_info(t)
    info = info.rename(columns={'WINDCODE':'Ticker'})
    info = info.set_index('Ticker')
    infolist.append(info)

infodf = pd.concat(infolist, axis = 0)

stock_describe = IO.read_data([20170101,21000101], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
stock_describe = stock_describe.reset_index()[['Ticker','S_INFO_COMPCODE']].rename(columns = {'Ticker':'stockcode','S_INFO_COMPCODE':'COMPCODE'})

infodf = pd.merge(stock_describe, infodf.reset_index(), how = 'right').set_index('Ticker')
# infodf.loc[~infodf.index.duplicated()]
infodf.to_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/CHINA_CONVERTIBLE_BOND_INFO.csv')