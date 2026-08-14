# coding: utf-8
# Author：fengchi863
# Date ：2024/3/22 10:50

import sys
sys.path.append('/data/user/015614/Lucien')
import pandas as pd
import numpy as np
from dataApi import tradeDate
from tqdm import tqdm
from dataApi import stockList, getData
import decimal
from xquant.factordata import FactorData
import datetime as dt

fd = FactorData()

def calc_limit_max(pre_close):
    cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3'), pre_close.columns.tolist()))
    not_cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3') - 1, pre_close.columns.tolist()))
    if pre_close.index[0] >= 20200824:
        pre_close_cyb = pre_close[cyb]
        pre_close_not_cyb = pre_close[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]
        return limit_max
    elif pre_close.index[-1] < 20200824:
        limit_max = (pre_close * 100 * 1.1 + 0.5).apply(np.floor) / 100
        return limit_max
    else:
        after_20200824 = pre_close.loc[20200824:]
        before_20200824 = pre_close.loc[:20200823]
        limit_max_before_20200824 = (before_20200824 * 100 * 1.1 + 0.5).apply(np.floor) / 100

        pre_close_cyb = after_20200824[cyb]
        pre_close_not_cyb = after_20200824[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max_after_20200824 = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]

        limit_max = pd.concat([limit_max_before_20200824, limit_max_after_20200824], axis=0)
    return limit_max

def round_(x, n=0):
    # 四舍五入有效数字，python其他四舍五入算法不精确
    if n>0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1'%('0'*(n-1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

if len(sys.argv) > 1:
    today_date = sys.argv[1]
    print(f'当前计算{today_date}...')
else:
    today_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]

root_path = '/data/user/015614/daily/basic/basic_wind_sw_history_everyday/BlockData/daily_Wind&SW/'
basic_sample = pd.read_pickle('/data/user/018107//share_file/for_fc/europa_basic_index_20160101_20250510.pkl')

# stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=1, least_normal_days=1, no_pause=True, least_recover_days=0, start_date=int(today_date), end_date=int(today_date))
stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=1, least_normal_days=1, no_pause=True, least_recover_days=0, start_date=int(20160101), end_date=int(today_date))
stk_list = stk_pool.iloc[-1].index.tolist()
pre_close = getData.get_daily_1factor('pre_close', date_list=[today_date], code_list=stk_list)
limit_max = calc_limit_max(pre_close)
close = getData.get_daily_1factor('close', date_list=[today_date], code_list=stk_list)
high = getData.get_daily_1factor('high', date_list=[today_date], code_list=stk_list)
low = getData.get_daily_1factor('low', date_list=[today_date], code_list=stk_list)

#%% 改为手动计算，不然Basic_zt生成时间太晚了，由于涨停价的计算方式问题，肯定已经不判断ST股涨停了
# high <= limit_max 为了剔除上市第一天，那类没有涨跌幅限制的股票
limit_max_minus001 = (limit_max - 1 / 100).applymap(lambda x:round_(x, 2))
basic_zt = (high >= limit_max_minus001) & (low < limit_max_minus001) & (high <= limit_max)

zt_list = list(map(stockList.trans_int2windcode, basic_zt.iloc[-1][basic_zt.iloc[-1]].index.tolist()))
basic_zt_indexes = pd.MultiIndex.from_product([[pd.to_datetime(str(today_date))], zt_list]).tolist()

europa_df = pd.DataFrame(basic_zt_indexes, columns=['dt', 'stk_code'])
europa_df['trade_date'] = europa_df['dt'].map(lambda x: x.strftime('%Y%m%d'))
europa_df = europa_df.query('trade_date >= @today_date & trade_date <= @today_date')

# date_list = tradeDate.get_date_range(20160101, 20211231)
# date_list = tradeDate.get_date_range(20220101, 20220531)
# date_list = tradeDate.get_date_range(20160101, 20240221)
# date_list = tradeDate.get_date_range(20160105, 20240513)
# date_list = tradeDate.get_date_range(today_date, today_date)
date_list = tradeDate.get_date_range(20250110, 20250510)

for _dat in tqdm(date_list):
    pre_dat_ = tradeDate.get_pre_trade_date(_dat) if _dat >= 20160105 else 20160104
    concept_df = pd.read_pickle(root_path + f'{pre_dat_}.pkl')
    try:
        cur_samples = basic_sample.loc[pd.to_datetime(str(_dat))].index.tolist()
    except:
        print('Error', _dat)
        continue
    concept_df = concept_df.loc[cur_samples]

    concept_df2 = concept_df.copy()
    concept_np = concept_df.values
    concept_np2 = concept_df2.values
    check = concept_np2.dot(concept_np.T)
    res_df = pd.DataFrame(check, index=concept_df2.index.tolist(), columns=concept_df.index.tolist())

    # res_df.to_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
    # res_df.to_pickle(f'/data/user/015614/shared/for_zwh/d20240410_europa_concept_cross_num/{_dat}.pkl')
    res_df.to_pickle(f'/data/group/800463/data/concept_data/europa/20250512/{_dat}.pkl')
    print(_dat, res_df.sum().sum())

# counter = pd.Series(index=date_list)
# for _dat in date_list:
#     try:
#         res = pd.read_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
#         counter.loc[_dat] = res.sum().sum()
#     except:
#         counter.loc[_dat] = 0

from scipy.io import mmread, mmwrite, mminfo
# from scipy.sparse import coo_matrix
#
# coo = coo_matrix((res_df.values.reshape(-1), (list(np.arange(res_df.shape[1])) * res_df.shape[0], list(np.arange(res_df.shape[0])) * res_df.shape[1])), shape=res_df.shape)
