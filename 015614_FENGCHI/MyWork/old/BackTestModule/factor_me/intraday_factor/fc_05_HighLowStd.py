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
# 3、根据日内时间信息，计算每分钟最高价和最低价在一个固定时间窗口内的序列的波动率的差异；
# 4、rolling_std(high) / rolling_std(low)
# 4、根据分钟因子横截面排序，取96%分位数以上进行买入，4%以下进行卖出；

pct_qrr_up = 0.96  # M
pct_qrr_down = 0.04  # N
max_holding_day = 3  # P
order_holding = 5  # Q

start = 20170101  # start_time
end = 20191231  # end_time
trading_day_all = s.tradingday(20160101, 20191231, \
                               frequency='DAY', dayType=None, dateType='TRADINGDAYS')
trading_day_all = list(map(int, trading_day_all))
trading_day = [item for item in trading_day_all if ((item >= start) & (item <= end))]
start, end = trading_day[0], trading_day[-1]

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

# 筛选
bool_clean = new_stock_pool.loc[close.index] & bool_pct_chg_up & \
             bool_pct_chg_down

# 定义因子信号
print('start to calculate factor')

def get_daily_factor(date):
    print(date)
    start_time = date * 10000 + 930
    end_time = date * 10000 + 1500
    temp_bool_clean = bool_clean.loc[date]
    temp_minutest_high = get_minute_1factor('high', start_datetime=start_time, end_datetime=end_time,
                                            code_list=code_list)
    temp_minutest_low = get_minute_1factor('low', start_datetime=start_time, end_datetime=end_time,
                                           code_list=code_list)
    temp_minutest_high_std = temp_minutest_high.rolling(30).std()
    temp_minutest_low_std = temp_minutest_low.rolling(30).std()
    high_low_std = temp_minutest_high_std / temp_minutest_low_std

    highBand = high_low_std.quantile(pct_qrr_up, axis=1)
    lowBand = high_low_std.quantile(pct_qrr_down, axis=1)
    # 小的买入，大的卖出
    factor_df = high_low_std.sub(lowBand, axis=0)
    factor_df.where(factor_df < 0, np.nan, inplace=True)
    factor_df.where(factor_df.isna(), 1, inplace=True)

    factor_df2 = high_low_std.sub(highBand, axis=0)
    factor_df2.where(factor_df2 > 0, 0.0, inplace=True)
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
                 'fc_05_HighLowStd_M%.2f_N%.2f.pkl' % (pct_qrr_up, pct_qrr_down))

print(time.time() - e1)
e1 = time.time()

# 定义因子回测对象
factor_test = FactorBackTest(factor, max_holding_day=max_holding_day, \
                             order_holding=order_holding)
print('因子回测初始化时间：', time.time() - e1)

# 并行回测
factor_test.evaluation(32)
factor_test.result_output('fc_05_HighLowStd_M%.2f_N%.2f' % (pct_qrr_up, pct_qrr_down), \
                          '/data/group/800319/junkData/temp_factor_by_fc/result/')

res = factor_test.evaluation_result.T
resDay = factor_test.evaluation_result_daily
netValue = factor_test.net_value
trading_records = factor_test.trading_record
