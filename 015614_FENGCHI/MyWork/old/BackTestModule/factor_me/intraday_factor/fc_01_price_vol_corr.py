# coding: utf-8
# Author：fengchi863
# Date ：2020/2/25 16:46

import pandas as pd
import numpy as np
import os
# os.chdir('/data/group/800319/BackTestModule/')
from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import sys
sys.path.append('/data/group/800319')
from dataApi.getData import get_minute_1factor,get_daily_1factor
from dataApi.stockList import clean_stock_list
from multiprocessing import Pool

# 因子逻辑：
# 1.在排序池中（1800）计算所有股票超额收益率相对均值的波动率倍数；
# 2.波动率倍数top5%，bottom5%买入；
# 3.买入卖出股票限制在入选池中。

pct_qrr_up = 0.95 # M
pct_qrr_down = 0.1 # N

start = 20170101 # start_time
end = 20191231 # end_time
trading_day_all = s.tradingday(20160101, 20191231, \
                           frequency='DAY', dayType=None, dateType='TRADINGDAYS')
trading_day_all = list(map(int, trading_day_all))
trading_day = [item for item in  trading_day_all if ((item >= start) & (item <= end)) ]
start, end = trading_day[0],trading_day[-1]

factor_name = 'fc_04_minute_alpha'
indexcode = 'ZZ500'
# pcnt = 0.05
e1 = time.time()

#定义股票池
# stock_pool50 = get_index_comp(start,end,'SH50')
# stock_pool300 = get_index_comp(start,end,'HS300')
stock_pool500 = get_index_comp(start,end,'ZZ500')
# stock_pool1000 = get_index_comp(start,end,'ZZ1000')

# 排序池
# stock_pool_all = clean_stock_list(no_ST=True, stock_list= 'COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
#                  no_limit_up=False, no_limit_down=False,
#                  address='/data/group/800319/junkData/daily')
# 使用陶鑫的股票池
new_stock_pool = pd.read_hdf('/data/group/800319/New_stock_pool.h5','New_stock_pool')
new_stock_pool = new_stock_pool.replace(1, True).replace(0, False)
# stock_list must in (ALL, COMMON, HS300, ZZ500, ZZ1000)

# 入选池
stock_pool_in = stock_pool500[start]
stock_pool_in = [item for item in stock_pool_in if item in new_stock_pool.columns]

codeList = list(new_stock_pool.columns)

#日频高开低收
# 不复权价格
close = get_daily_1factor('close', date_list= trading_day, code_list=codeList, type='stock')
# 前复权价格，计算区间涨跌幅
close_adj = get_daily_1factor('close_badj', date_list= trading_day_all, code_list=codeList, type='stock')
pctb = close_adj.pct_change(60).loc[close.index].fillna(0)
del close_adj
# pe_ttm
pe = get_daily_1factor('pe_ttm', date_list= trading_day, code_list=codeList, type='stock')

# 可买入股票前60日涨跌幅在全市场分位数处于 10% - 80%
pctb_up = pctb.quantile(0.8,axis =1)
pctb_down = pctb.quantile(0.1,axis =1)

bool_pctb_up = pctb.sub(pctb_up, axis=0) < 0
bool_pctb_down = pctb.sub(pctb_down, axis=0) > 0

# 可买入股票  0 < pe < 300
bool_pe_up = pe < 300
bool_pe_down = pe > 0

# 筛选
bool_clean = new_stock_pool.loc[close.index] & bool_pctb_up & \
             bool_pctb_down & bool_pe_up & bool_pe_down

# 定义因子信号
print('start to calculate factor')
factor_df_list = []
# for datei in trading_day:
def get_daily_factor(datei):
    print(datei)
    begi = datei * 10000 + 930
    endi = datei * 10000 + 1500
    bool_cleani = bool_clean.loc[datei]
    # 不复权分钟收盘价
    temp_minutest_vol = get_minute_1factor('vol', start_datetime = begi, end_datetime = endi,
                                    code_list = codeList)
    temp_minutest_price = get_minute_1factor('close', start_datetime=begi, end_datetime=endi,
                                                code_list=codeList)
    temp_minutest_pv_corr = temp_minutest_price.rolling(30).corr(temp_minutest_vol)
    pv_corr = temp_minutest_pv_corr

    highBand = pv_corr.quantile(pct_qrr_up,axis =1)
    lowBand = pv_corr.quantile(pct_qrr_down,axis =1)
    # 1买入 -1卖出
    factor_df = pv_corr.sub(lowBand ,axis = 0)
    factor_df.where(factor_df < 0, np.nan, inplace=True)
    factor_df.where(factor_df.isna(), 1, inplace=True)

    factor_df2 = pv_corr.sub(highBand, axis = 0)
    factor_df2.where(factor_df2 > 0, 0.0, inplace=True)
    factor_df2.where(factor_df2 <=0, -1, inplace = True)

    factor_df.fillna(factor_df2,inplace = True)
    factor_df.fillna(0,inplace = True)

    factor_df.iloc[:30,:] = 0
    factor_df.iloc[-3:, :] = 0

    stk_clean = bool_cleani[~bool_cleani].index.intersection(factor_df.columns)
    factor_df[stk_clean] = 0
    return factor_df

pool = Pool(32)
factor_df_list = pool.map_async(get_daily_factor, trading_day)
pool.close()
pool.join()
factor_df = pd.concat(factor_df_list.get(), axis=0)
factor_df.sort_index(inplace=True)

factor_df = factor_df[stock_pool_in]
# del factor_df2
factor_df = factor_df.astype(int)
factor_df.index = [x*10000 + y for x,y in  factor_df.index]
# factor_df.to_hdf('/data/group/800319/junkData/temp_factor_by_fc/alpha.h5', 'alpha')

factor_df.to_pickle('/data/group/800319/junkData/temp_factor_by_fc/' + \
                    'fc_01_PV_corr_M%.2f_N%.2f.pkl'%(pct_qrr_up, pct_qrr_down))

# del temp_minutest_data
print(time.time() - e1)
e1 = time.time()

#定义因子回测对象
factor_test = FactorBackTest(factor_df)
print(time.time()-e1)
# del factor_df
#并行回测
factor_test.evaluation(32)
factor_test.result_output('fc_01_PV_corr_M%.2f_N%.2f.pkl'%(pct_qrr_up, pct_qrr_down), \
                          '/data/group/800319/junkData/temp_factor_by_fc/')

res = factor_test.evaluation_result.T
resDay = factor_test.evaluation_result_daily
netValue = factor_test.net_value
trading_records = factor_test.trading_record