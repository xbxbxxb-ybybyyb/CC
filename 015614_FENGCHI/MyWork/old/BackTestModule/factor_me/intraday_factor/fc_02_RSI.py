# coding: utf-8
# Author：fengchi863
# Date ：2020/2/21 10:01

import pandas as pd, numpy as np
import os
os.chdir('/data/group/800319/BackTestModule/')
from QuickFactorEvaluationBackTest import FactorBackTest
from config import *
from dataApi import getData, stockList, tradeDate
from dataApi.tradeDate import trade_minutes
import time
import copy

## parameters
DOWN_ALPHA = 0.01
UP_ALPHA = 0.99
UP_MINUTE_FACTOR = 0.995
DOWN_MINUTE_FACTOR = 0.04
NUM_DAYS_ALPHA = 5 # 日间超额计算滚动天数
MINUTE_ROLLING = 30
max_holding_day = 3  # P
order_holding = 5  # Q

## 回测参数
start = 20170101
end = 20191231
e1 = time.time()

## 股票池
start_date = 20170101  # start_time
end_date = 20191231  # end_time
trading_day_all = s.tradingday(20160101, 20191231, \
                               frequency='DAY', dayType=None, dateType='TRADINGDAYS')
trading_day_all = list(map(int, trading_day_all))
trading_day = [item for item in trading_day_all if ((item >= start_date) & (item <= end_date))]
start_date, end_date = trading_day[0], trading_day[-1]

# 使用陶鑫的股票池
new_stock_pool = pd.read_hdf('/data/group/800319/New_stock_pool.h5', 'New_stock_pool')
new_stock_pool = new_stock_pool.replace(1, True).replace(0, False)
code_list = list(new_stock_pool.columns)

### 构建日间因子，比如均线类、超额类
## 获取bench每一天的涨跌幅
bench_close = getData.get_daily_1factor('close', date_list=trading_day, \
                                        code_list=['ZZ500'], type='bench')
bench_pct_chg = bench_close['ZZ500'] / bench_close['ZZ500'].shift(1) - 1

stock_daily_close = getData.get_daily_1factor('close_badj', date_list=trading_day, \
                                              code_list=code_list, type='stock')
stock_daily_pre_close = getData.get_daily_1factor('pre_close_badj', date_list=trading_day, \
                                                  code_list=code_list, type='stock')
stock_daily_pct_chg = stock_daily_close / stock_daily_pre_close - 1

## 计算每只股票每日相对中证500的超额
stock_daily_alpha_valeus = stock_daily_pct_chg.values - \
                            bench_pct_chg.values.reshape(bench_pct_chg.shape[0],-1)
stock_daily_alpha = pd.DataFrame(stock_daily_alpha_valeus, index=stock_daily_pct_chg.index,\
                                columns=stock_daily_pct_chg.columns)

## 计算前两日超额
stock_daily_alpha_pre2days = stock_daily_alpha.rolling(NUM_DAYS_ALPHA).sum()
stock_daily_alpha_pre2days_rank_pct = stock_daily_alpha_pre2days.rank(ascending=False, axis=1, pct=True).shift(1)
# 反转，买跌
stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct < DOWN_ALPHA] = 1 # 买
# stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct > UP_ALPHA] = -1 # 不买
NonFactor_alpha_pre2days =  stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct < DOWN_ALPHA].fillna(0) + \
                  stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct > UP_ALPHA].fillna(0)

### 获取数据
## 计算RSI指标，参数：N分钟，阈值：0.05-0.95
e1 = time.time()
factor = pd.DataFrame()

def get_stock_factor(stock):
    print(stockList.trans_int2windcode(stock))
    f = pd.HDFStore('/data/group/800319/junkData/minuteByStock/' + str(stock) + '.h5', 'r')
    stock_indaydata = f[f.keys()[0]][(f[f.keys()[0]]['date'] >= start) * (f[f.keys()[0]]['date'] <= end)]
    stock_indaydata['datetime'] = stock_indaydata['date'] * 10000 + stock_indaydata['time']
    stock_indaydata = stock_indaydata.set_index('datetime').drop(['date', 'time'], axis=1)
    stock_indaydata['pct_chg'] = stock_indaydata['close'] / stock_indaydata['open'] - 1
    stock_indaydata['pct_chg_1'] = stock_indaydata['pct_chg'].apply(lambda x: x if x > 0 else 0)
    stock_indaydata['pct_chg_0'] = stock_indaydata['pct_chg'].apply(lambda x: x if x < 0 else 0)
    ## 建立个股的因子值
    factor_single_stock = pd.DataFrame(index=stock_indaydata.index, columns=[stock])
    up_sum = stock_indaydata['pct_chg_1'].shift(1).rolling(MINUTE_ROLLING).sum()
    down_sum = stock_indaydata['pct_chg_0'].shift(1).rolling(MINUTE_ROLLING).sum()
    rs = up_sum / down_sum
    factor_single_stock[stock] = 100 - 100 / (1 + rs)
    return factor_single_stock

pool = Pool(32)
factor_df_list = pool.map_async(get_stock_factor, new_stock_pool.columns.tolist())
pool.close()
pool.join()
factor = pd.concat(factor_df_list.get(), axis=1)
factor.sort_index(inplace=True)
print(time.time() - e1)

factor2 = copy.deepcopy(factor) # 深复制
del_time = list(filter(lambda x: x < 1000, trade_minutes)) + [1457, 1458, 1459, 1500]

# 把不属于当日个股的因子值变为None,把集合竞价时刻的因子变为None
# for date in trading_day:
#     del_stock = list(set(list(factor2.columns)) - set(ZZ800_stock_pool_dict[date]))
#     factor2.loc[factor2[del_stock][(factor2.index / 10000).astype(int) == date].index, del_stock] = None
factor2[(factor2.index % 10000).isin(del_time)] = None

## 大的开仓，小的平仓
factor_signal = factor2.rank(ascending=False, axis=1, pct=True)
factor_signal[factor_signal > UP_MINUTE_FACTOR] = 1
factor_signal[factor_signal < DOWN_MINUTE_FACTOR] = -1
factor_signal_df = factor_signal[factor_signal > UP_MINUTE_FACTOR].fillna(0) + \
                   factor_signal[factor_signal < DOWN_MINUTE_FACTOR].fillna(0)

values = factor_signal_df.values.reshape(len(trading_day),242,-1).swapaxes(0,1) + \
                NonFactor_alpha_pre2days.values
values = values.swapaxes(0,1)
values = values.reshape(len(trading_day)*242, -1)
new_factor_signal_df = pd.DataFrame(values, index=factor_signal_df.index, columns=factor_signal_df.columns)

new_factor_signal_df[new_factor_signal_df==2] = 1
new_factor_signal_df[new_factor_signal_df==-1] = -1
new_factor_signal_df = new_factor_signal_df[new_factor_signal_df==1].fillna(0) + \
                        new_factor_signal_df[new_factor_signal_df==-1].fillna(0)

### 临时保存
factor2.to_pickle('/data/group/800319/junkData/temp_factor_by_fc/factor_rsi.pkl')
new_factor_signal_df.to_pickle('/data/group/800319/junkData/temp_factor_by_fc/factor/'+ \
                               'fc_02_rsi.pkl')

## 因子测试
e1 = time.time()
temp_factor = FactorBackTest(new_factor_signal_df, max_holding_day=max_holding_day, \
                             order_holding=order_holding)
print(time.time()-e1)

e1 = time.time()
temp_factor.evaluation(32)
print(time.time()-e1)

evaluation_result = temp_factor.evaluation_result
temp_factor.result_output('fc_02_rsi', \
                          '/data/group/800319/junkData/temp_factor_by_fc/result/')