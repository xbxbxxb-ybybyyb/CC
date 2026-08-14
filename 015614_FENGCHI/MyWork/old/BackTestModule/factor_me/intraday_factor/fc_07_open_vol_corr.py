# coding: utf-8
# Author：fengchi863
# Date ：2020/2/24 13:41

import pandas as pd
import numpy as np
import os
from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import sys

sys.path.append('/data/group/800319')
from dataApi.getData import get_minute_1factor, get_daily_1factor
from multiprocessing import Pool

# 因子逻辑：
# 1、日间股票池筛选；
# 2、筛选出日前的涨跌幅限制在10%-80%区间内；
# 3、根据日内时间信息，按分钟进行计算，factor = -1*correlation(open,volume,len_window)；
# 4、根据分钟因子横截面排序，取98%分位数以上进行买入，8%以下进行卖出；

# 部分参数
pct_qrr_up = 0.98  # M
pct_qrr_down = 0.08  # N
max_holding_day = 3  # P
order_holding = 5  # Q
len_window = 30 # R

start_date = 20170101  # start_time
end_date = 20191231  # end_time
trading_day_all = s.tradingday(20160101, 20191231, \
                               frequency='DAY', dayType=None, dateType='TRADINGDAYS')
trading_day_all = list(map(int, trading_day_all))
trading_day = [item for item in trading_day_all if ((item >= start_date) & (item <= end_date))]
start_date, end_date = trading_day[0], trading_day[-1]

factor_name = ''
indexcode = 'ZZ500'
e1 = time.time()

# 使用陶鑫的股票池
new_stock_pool = pd.read_hdf('/data/group/800319/New_stock_pool.h5', 'New_stock_pool')
new_stock_pool = new_stock_pool.replace(1, True).replace(0, False)
code_list = list(new_stock_pool.columns)

# 日频高开低收
# 不复权价格
close = get_daily_1factor('close', date_list=trading_day, code_list=code_list, type='stock')
close_adj = get_daily_1factor('close_badj', date_list=trading_day_all, code_list=code_list, type='stock')
s_pct_chg = close_adj.pct_change(60).loc[close.index].fillna(0)
del close_adj

# 可买入股票前60日涨跌幅在全市场分位数处于 10% - 80%
pct_chg_up = s_pct_chg.quantile(0.8, axis=1)
pct_chg_down = s_pct_chg.quantile(0.1, axis=1)

bool_pct_chg_up = s_pct_chg.sub(pct_chg_up, axis=0) < 0
bool_pct_chg_down = s_pct_chg.sub(pct_chg_down, axis=0) > 0

# 筛选日间股票池
bool_clean = new_stock_pool.loc[close.index] & bool_pct_chg_up & \
             bool_pct_chg_down

# 定义因子信号
print('start to calculate factor')

def get_daily_factor(date):
    print(date)
    begin = date * 10000 + 930
    end = date * 10000 + 1500
    temp_bool_clean = bool_clean.loc[date]

    # 数据准备
    temp_minute_vol = get_minute_1factor('vol', start_datetime=begin, \
                                         end_datetime=end, code_list=code_list)
    temp_minute_open = get_minute_1factor('open', start_datetime=begin, \
                                           end_datetime=end, code_list=code_list)

    # 计算因子
    open_vol_corr = -1 * temp_minute_open.rolling(len_window).corr(temp_minute_vol)

    high_band = open_vol_corr.quantile(pct_qrr_up, axis=1)
    low_band = open_vol_corr.quantile(pct_qrr_down, axis=1)

    # 因子值越小，越呈现出量增价增的状态，这时买入，反之
    factor_df = open_vol_corr.sub(low_band, axis=0)
    factor_df.where(factor_df < 0, np.nan, inplace=True)
    factor_df.where(factor_df.isna(), 1, inplace=True)

    factor_df2 = open_vol_corr.sub(high_band, axis=0)
    factor_df2.where(factor_df2 > 0, 0, inplace=True)
    factor_df2.where(factor_df2 <= 0, -1, inplace=True)

    factor_df.fillna(factor_df2, inplace=True)
    factor_df.fillna(0, inplace=True)

    factor_df.iloc[:30, :] = 0
    factor_df.iloc[-3:, :] = 0

    stk_clean = temp_bool_clean[~temp_bool_clean].index.intersection(factor_df.columns)
    factor_df[stk_clean] = 0
    return factor_df

pool = Pool(32)
factor_df_list = pool.map_async(get_daily_factor, trading_day)
pool.close()
pool.join()
factor = pd.concat(factor_df_list.get(), axis=0)
factor.sort_index(inplace=True)

## 计算买入信号和卖出信号的比例
pct_buy_signal = factor[factor > 0].sum().sum() / (factor.shape[0] * factor.shape[1])
pct_sell_signal = factor[factor < 0].sum().sum() / (factor.shape[0] * factor.shape[1])

factor = factor.astype(int)
factor.index = [x * 10000 + y for x, y in factor.index]

factor.to_pickle('/data/group/800319/junkData/temp_factor_by_fc/factor/' + \
                 'fc_07_open_vol_corr_M%.2f_N%.2f_P%d_Q%d.pkl' % \
                 (pct_qrr_up, pct_qrr_down, max_holding_day, order_holding))

print('因子计算时间：', time.time() - e1)
e1 = time.time()

# 定义因子回测对象
factor_test = FactorBackTest(factor, max_holding_day=max_holding_day, \
                             order_holding=order_holding)
print('因子回测初始化时间：', time.time() - e1)

# 并行回测
e1 = time.time()
factor_test.evaluation(32)
factor_test.result_output('fc_07_open_vol_corr_M%.2f_N%.2f_P%d_Q%d' % \
                          (pct_qrr_up, pct_qrr_down, max_holding_day, order_holding), \
                          '/data/group/800319/junkData/temp_factor_by_fc/result/')
print('因子回测时间：', time.time() - e1)

res = factor_test.evaluation_result.T
resDay = factor_test.evaluation_result_daily
netValue = factor_test.net_value
trading_records = factor_test.trading_record
