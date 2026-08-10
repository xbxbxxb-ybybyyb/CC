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
    if symbol[-2:] not in ['SH', 'SZ']:
        return
    print(symbol)
    result_min = bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'K_1MIN')
    if len(result_min) == 0:
#        print(symbol, date, 'no data')
        return
    result_min['dt'] = result_min.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
    result_min = result_min.drop(droplist, axis = 1)
    result_min['Ticker'] = symbol
    result_min = result_min.set_index(['dt','Ticker']).rename(columns = column_name_dict)
    if symbol.endswith('SH'):
        result_min['volume'] = result_min['volume'] * 10
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

def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def get_stk_minute_by_date(date):
    stk_minute_data = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/%s.pkl' % str(date), compression='gzip')
    stk_minute_data = stk_minute_data.reset_index()
    stk_minute_data['Ticker'] = stk_minute_data.Ticker.apply(lambda x:ticker_match(x))
    stk_minute_data['dt'] = stk_minute_data['dt'] * 1E6 + stk_minute_data['minute'] * 100
    stk_minute_data['dt'] = pd.to_datetime(stk_minute_data['dt'].astype('int64'), format='%Y%m%d%H%M%S')
    stk_minute_data = stk_minute_data.rename(columns = {'Ticker':'stock_code','amt':'amount'}).set_index(['dt','stock_code']).add_suffix('_stk')
    return stk_minute_data
            
droplist = ['MDRecordID', 'KLineType', 'SecurityID', 'HTSCSecurityID', 'MDDate',
       'MDTime','PeriodType', 'IOPV', 'OpenInterest', 'SettlePrice']
column_name_dict = {'OpenPx':'open', 'ClosePx':'close', 'HighPx':'high', 'LowPx':'low',  'TotalVolumeTrade':'volume', 'TotalValueTrade':'amount'}

savepath = '/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/MINUTE/per_date/'
sdate,edate,cdate_list = check_update_date()

def minute_flag_check(date):
    path1 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_MINUTE.success'
    return os.path.exists(path1)


flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(edate) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(edate) + '_' + 'kzz_minute.start'
with open(flag_path_start,'w') as file:
    pass 

print('------wait minute flag')
while True:
    if minute_flag_check(sdate):
        break
    time.sleep(60)
print('flag check finished!')



print('update kzz minute data')
result_list = []
for x in cdate_list:
    result_list.append(get_kzz_data_by_date(x))
    
append_df = pd.concat(result_list, axis = 0).sort_index()
IO.pd_hdf5_writer(append_df, '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE.h5', dataset = 'CHINA_CONVERTIBLE_BOND_MINUTE', append = True)

# 以上为每日更新可转债分钟数据，以下为基本信息表
print('update kzz info csv')
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
infodf['isAstock'] = infodf.stockcode.apply(lambda x:x.startswith('A'))
infodf = infodf.loc[infodf.isAstock == False].drop(['isAstock'], axis = 1)
infodf = infodf.loc[~infodf.index.duplicated()]
infodf.to_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/CHINA_CONVERTIBLE_BOND_INFO.csv')

# 以下为更新正股分钟数据
print('update kzz stk minute data')
ap_tickerlist = append_df.index.get_level_values(1).unique().tolist()

kzz_stock = pd.read_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/CHINA_CONVERTIBLE_BOND_INFO.csv', index_col=0)[['stockcode']]
kzz_stock_dict = kzz_stock.to_dict()['stockcode']
kzz_standard = append_df[['NumTrades']].reset_index()
kzz_standard['stock_code'] = kzz_standard['Ticker'].apply(lambda x:kzz_stock_dict[x] if x in list(kzz_stock_dict.keys()) else np.nan)
kzz_standard = kzz_standard.dropna(subset = ['stock_code'])
kzz_standard = kzz_standard.set_index(['dt','stock_code'])

stk_minute_list = []
for date in cdate_list:
    stk_minute_list.append(get_stk_minute_by_date(date))
stk_minute_data = pd.concat(stk_minute_list, axis = 0)

kzz_stk = kzz_standard.join(stk_minute_data, how = 'left')
kzz_stk = kzz_stk.reset_index().drop(['stock_code','NumTrades','minute_stk'], axis = 1).set_index(['dt','Ticker'])

append_df = append_df.join(kzz_stk, how = 'left')
IO.pd_hdf5_writer(append_df, '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE_AND_STOCK.h5', dataset='CHINA_CONVERTIBLE_BOND_MINUTE_AND_STOCK', append = True)

flag_path_start = flag_root + str(edate) + '_' + 'kzz_minute.success'
with open(flag_path_start,'w') as file:
    pass 
