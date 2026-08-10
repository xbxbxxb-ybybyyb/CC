import sys
sys.path.insert(4, '/data/user/016700/')
import pandas as pd
import numpy as np
from shutil import copyfile
import os
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pickle
from functools import partial
from joblib import Parallel, delayed
from operators_cc import *
import datetime
import warnings
warnings.filterwarnings('ignore')
import bottleneck as bk
import datetime
from multifactor.data.utils import *
from datetime import timedelta
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

def rr(num):
    if num == 0:
        return np.nan
    else:
        return num
_, end_date, _ = check_update_date()
sdate,eedate,cdate_list = check_update_date(20240101, end_date)


rcdate1 = str(cdate_list[-1])
rcdate2 = str(cdate_list[-1])

_3, _3, rdate_list = check_update_date(int(rcdate1), int(rcdate2))
date_pairs = []
for i, date in enumerate(cdate_list):
    if i > 0:
        date_pairs.append([cdate_list[i-1], cdate_list[i]])
print(rcdate2)
future_data_dict = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')
vol_ic = ((future_data_dict['close'].between_time('0930', '1456')/future_data_dict['close'].between_time('0930', '1456').shift(1) - 1).rolling(30, min_periods = 15).std()[future_data_dict['recent_month_mask']]).sum(axis = 1)
vol_if = ((future_data_dict['close_if'].between_time('0930', '1456')/future_data_dict['close_if'].between_time('0930', '1456').shift(1) - 1).rolling(30, min_periods = 15).std()[future_data_dict['recent_month_mask']]).sum(axis = 1)
vol_im = ((future_data_dict['close_im'].between_time('0930', '1456')/future_data_dict['close_im'].between_time('0930', '1456').shift(1) - 1).rolling(30, min_periods = 15).std()[future_data_dict['recent_month_mask']]).sum(axis = 1)


volume_ic = ((future_data_dict['volume'].between_time('0930', '1456'))[future_data_dict['recent_month_mask']]).sum(axis = 1)
volume_if = ((future_data_dict['volume_if'].between_time('0930', '1456'))[future_data_dict['recent_month_mask']]).sum(axis = 1)
volume_im = ((future_data_dict['volume_im'].between_time('0930', '1456'))[future_data_dict['recent_month_mask']]).sum(axis = 1)



hic = pd.DataFrame()
hif = pd.DataFrame()
him = pd.DataFrame()
for item in cdate_list:
    try:
        tic = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/IC/CONCAT/_all_total_trade_detail.csv'%item)
        hic = pd.concat([hic, tic])
    except Exception as e:
        print(item, e)
    try:
        tif = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/IF/CONCAT/_all_total_trade_detail.csv'%item)
        hif = pd.concat([hif, tif])
    except Exception as e:
        print(item, e)
    try:    
        tim = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/IM/CONCAT/_all_total_trade_detail.csv'%item)
        him = pd.concat([him, tim])
    except Exception as e:
        print(item, e)
            
        
        
hic = hic.reset_index()
hif = hif.reset_index()
him = him.reset_index()

hic['open_time'] = pd.to_datetime(hic['open_time'])
hic['close_time'] = pd.to_datetime(hic['close_time'])


hif['open_time'] = pd.to_datetime(hif['open_time'])
hif['close_time'] = pd.to_datetime(hif['close_time'])


him['open_time'] = pd.to_datetime(him['open_time'])
him['close_time'] = pd.to_datetime(him['close_time'])

hic = hic.set_index('open_time').dropna(how = 'all', axis = 1)
hif = hif.set_index('open_time').dropna(how = 'all', axis = 1)
him = him.set_index('open_time').dropna(how = 'all', axis = 1)

hic = drop_dup(hic)
hif = drop_dup(hif)
him = drop_dup(him)

hic.sort_values(by = 'profit_intradeal').to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/ic.xlsx')

hif.sort_values(by = 'profit_intradeal').to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/if.xlsx')

him.sort_values(by = 'profit_intradeal').to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/im.xlsx')




vwap_ic = future_data_dict['vwap'][future_data_dict['recent_month_mask']].sum(axis = 1)
vwap_if = future_data_dict['vwap_if'][future_data_dict['recent_month_mask']].sum(axis = 1)
vwap_im = future_data_dict['vwap_im'][future_data_dict['recent_month_mask']].sum(axis = 1)

def getdt(a, b):
    strdate = str(a) + ' ' + str(b).split(' ')[-1]
    #return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')

    return pd.to_datetime(strdate)


def buysell(direct1):
    if direct1 == '卖':
        return -1
    else:
        return 1

di_slip = {}
cat_holder = []

df_ic = []
df_if = []
df_im = []


for cat in ['IC', 'IF', 'IM']:
    buy_df = pd.DataFrame()
    sell_df = pd.DataFrame()
    slip_holder = []
    
    for date1 in cdate_list:
        jyzh = []
        for item in os.listdir('/data/user/016700/Data/para/Mobius_%s/'%date1):
            if ('_' + cat in item) and (('_sim') not in item) and (('xlsx' in item)):
                temp = pd.read_excel('/data/user/016700/Data/para/Mobius_%s/'%date1 + item, encoding = 'gbk')
                jyzh.append(temp['买入交易账户'][0])

        if (cat == 'IC') or (cat == 'IM'):
            multiplier = 200
        elif cat == 'IF':
            multiplier = 300

        try:
            _ = pd.read_excel('/data/user/011477/order/O32/51606/Order/综合信息查询_委托流水_%s_fut.xls'%str(int(date1)), index_col = 0)
            _ = _.dropna(how = 'all', axis = 1)
            _ = _[~_['组合编号'].isna()]
            _['组合编号'] = _['组合编号'].astype(int)
            _ = _[(_['组合编号'].isin(jyzh))]

            _['委托时间'] = pd.to_datetime(_['委托时间'])

            _['dtt'] = _['委托时间'].apply(lambda x: x.hour * 100 + x.minute)

            _ = _[(_.dtt >= 935) & (_.dtt < 1458) & _['交易员'].isin(['张玮聪'])]

            

            futures_list = list(set([item1 for item1 in _['证券代码'] if cat in item1]))
            _['dt'] = _.apply(lambda x:getdt(x['发生日期'], x['委托时间']), axis = 1)
            _ = _.set_index('dt').sort_index()
            _ = _[_['证券代码'].isin(futures_list)]

            count = 0
            holder_start = []
            holder_end = []
            direction = []
            contracts = []

            for i,item2 in _.iterrows():
                direct = item2['委托方向'][0][0]
                contra = item2['证券名称']
                if count == 0:
                    holder_start.append(i)
                    direction.append(buysell(direct))
                    contracts.append(contra)
                else:
                    if (direct != direct_prev) or (contra != contra_prev) or ((i - holder_start[-1]).total_seconds() > 120):
                        if ((i - holder_start[-1]).total_seconds() <1.5):
                            pass
                        else:
                            holder_end.append(i_prev)
                            holder_start.append(i)
                            direction.append(buysell(direct))
                            contracts.append(contra)


                i_prev = i
                direct_prev = direct
                contra_prev = contra
                count = count + 1

            holder_end.append(i)

            res = list(zip(holder_start, holder_end, contracts, direction))
            #res = [[holder[i], holder[i + 1]] for i in list(range(0, len(holder), 2))]

            di = {}
            for future in futures_list:

                tickdf = pd.read_csv('/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/CSV/TICK/CHINA_FUTURES/ALL_CONTRACT/%s/%s.csv'%(future, date1))
                tickdf = tickdf.set_index('dt')
                tickdf.index = pd.to_datetime(tickdf.index)
                tickdf['amount'] = tickdf['TotalValueTrade'].diff()
                tickdf['volume'] = tickdf['TotalVolumeTrade'].diff()
                di[future] = tickdf

            stats_temp = []
            for i, item3 in enumerate(res):
                future_name = item3[-2]
                tickdf_temp = di[future_name]
                temp = tickdf_temp.loc[item3[0]:item3[1]]
                twap = temp['LastPx'].mean()
                vwap = temp['amount'].sum() / temp['volume'].sum() / multiplier
                temp_trade = _.loc[item3[0]:item3[1]]['成交金额'] / multiplier / _.loc[item3[0]:item3[1]]['累计成交数量']
                temp_trade[(temp_trade > temp_trade.mean() * 2)] = np.nan
                actual = temp_trade[temp_trade!=0].mean() 
                if abs(actual - twap) > 50:
                    temp_trade1 = temp_trade.copy()
                    continue
                direct = item3[-1]
                diff = -(direct * (actual - vwap))
                if abs(diff) > 5:
                    diff = np.nan
                stats_temp.append([item3[0], item3[1], vwap, twap, actual, direct, diff, _.loc[item3[0]:item3[1]]['累计成交数量'].sum(), future_name])
                if abs(twap - actual) > 10:
                    print([item3[0], item3[1], vwap, twap, actual, direct, diff, _.loc[item3[0]:item3[1]]['累计成交数量'].sum(), future_name])
            stats = pd.DataFrame(stats_temp, columns = ['open_time', 'close_time',  'vwap',  'twap', 'actual','direction','diff', 'deal_count', 'future_name'])
            stats[stats.actual > (stats.actual.mean() * 2)] = np.nan
            stats = stats.dropna(how = 'all', axis = 1)
            stats = stats[~stats.actual.isna()]
            #buy = stats[stats.direction == 1]
            #sell = stats[stats.direction == -1]
            
            #buy_slip = (buy['diff'] * buy['deal_count']).sum() / buy['deal_count'].sum()
            #sell_slip = (sell['diff'] * sell['deal_count']).sum() / sell['deal_count'].sum()
            #buy_df = pd.concat([buy_df, buy])
            #sell_df = pd.concat([sell_df, sell])
            
            slip_holder.append([date1, (stats['diff'] * stats['deal_count']).sum() / stats['deal_count'].sum(), stats['deal_count'].sum()])
            
        except Exception as e:
            print(date1, cat, e)
    if cat == 'IC':
        df_ic.append(slip_holder)
    if cat == 'IF':
        df_if.append(slip_holder)
    if cat == 'IM':
        df_im.append(slip_holder)
        
pd.DataFrame(df_ic[0], columns = ['date', 'slippage', 'deal_counts']).set_index('date').to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/daily/slippage/ic.xlsx')
pd.DataFrame(df_if[0], columns = ['date', 'slippage', 'deal_counts']).set_index('date').to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/daily/slippage/if.xlsx')
pd.DataFrame(df_im[0], columns = ['date', 'slippage', 'deal_counts']).set_index('date').to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/daily/slippage/im.xlsx')

volume_ic = future_data_dict['volume']
volume_if = future_data_dict['volume_if']
volume_im = future_data_dict['volume_im']

for cat in ['IC', 'IF', 'IM']:
    def calc(date1, cat = cat):

            path = '/data/user/016700/Data/para/Mobius_%s/'%str(date1)
            #tempdf = pd.read_excel(item, encoding = 'gbk', sheetname = 'InitialBasicParam')
            jyzh = []
            for item in os.listdir(path):
                if ('_' + cat in item) and (('_sim') not in item) and (('xlsx' in item)):
                    tempdf = pd.read_excel(path + item, encoding = 'gbk')
                    jyzh.append(tempdf['买入交易账户'][0])
            date = str(tempdf['交易日期'][0])
            jyzh = tempdf['买入交易账户'][0]
            trading_stats = pd.read_excel('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%date)
            trading_stats = trading_stats.loc[trading_stats['日期'].isna() == False]
            trading_stats['成交时间1'] = pd.to_datetime(trading_stats['成交时间'].apply(lambda x: (date + str(x).replace(':', ''))[:-2]))
            trading_stats = trading_stats[(trading_stats['组合编号'].isin([jyzh])) & (trading_stats['成交时间1'] >= pd.to_datetime(date + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(date + '1450'))].sort_values(by = '成交时间')

            contract_list = list(set(trading_stats['证券代码']))
            contract_list = sorted([item1 for item1 in contract_list if cat in item1])
            records = pd.DataFrame()

            if 'IC' in cat.upper():
                volume = volume_ic.copy()
            elif 'IF' in cat.upper():
                volume = volume_if.copy()
            else:
                volume = volume_im.copy()

            for contract in contract_list:
                contract_temp = contract.replace(cat, '') + '.CFE'
                ts_temp = trading_stats[trading_stats['证券代码'] == contract]
                record_temp1 = ts_temp['成交数量'].groupby(ts_temp['成交时间1']).count()
                record_temp2 = record_temp1 / volume[contract_temp].loc[record_temp1.index]
                records = pd.concat([records, record_temp2])
            return records

    with Pool(24) as pool:
        hholder = pool.map(calc, cdate_list)
    catdf_all = pd.concat(hholder)
    catdf_all.columns = [cat]
    catdf_all.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/pics/daily/proportion/proportion_%s.xlsx'%cat.lower())