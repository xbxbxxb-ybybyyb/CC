# coding: utf-8
# Author：fengchi863
# Date ：2020/2/21 10:01

import pandas as pd, numpy as np
import os
os.chdir('/data/group/800319/BackTestModule/')
from QuickFactorEvaluationBackTest import FactorBackTest
from config import ZZ800_daily_stock_pool
from config import *
from dataApi import getData, stockList, tradeDate
from dataApi.tradeDate import trade_minutes
import time
import copy

## parameters
DOWN_ALPHA = 0.01
UP_ALPHA = 0.99
UP_MINUTE_FACTOR = 0.99
DOWN_MINUTE_FACTOR = 0.01
NUM_DAYS_ALPHA = 5 # 日间超额计算滚动天数
MINUTE_ROLLING = 30

## 回测参数
start = 20170101
end = 20191231
e1 = time.time()

## 获取ZZ800股票池
# stock_pool = stock_pool=pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5','ZZ500')
ZZ800_daily_stock_pool = pd.DataFrame(ZZ800_daily_stock_pool).stack().reset_index()
ZZ800_daily_stock_pool['level_0'] = True
ZZ800_daily_stock_pool = ZZ800_daily_stock_pool.pivot('level_1', 0, 'level_0').\
                        fillna(False)
ZZ800_daily_stock_pool = ZZ800_daily_stock_pool[(ZZ800_daily_stock_pool.index >= start) * \
                                                (ZZ800_daily_stock_pool.index <= end)]
ZZ800_daily_stock_pool = ZZ800_daily_stock_pool.\
    drop(ZZ800_daily_stock_pool.loc[:,ZZ800_daily_stock_pool.sum(axis=0)==0].columns.tolist(),axis=1)
ZZ800_stock_pool_dict = {int(i): ZZ800_daily_stock_pool.\
    loc[i][ZZ800_daily_stock_pool.loc[i,:]==True].index.tolist() for i in ZZ800_daily_stock_pool.index}
trading_day = tradeDate.get_date_range(start, end, period='D')

### 构建日间因子，比如均线类、超额类
## 获取bench每一天的涨跌幅
bench_close = getData.get_daily_1factor('close', date_list=trading_day, \
                                        code_list=['ZZ500'], type='bench')
bench_pct_chg = bench_close['ZZ500'] / bench_close['ZZ500'].shift(1) - 1

stock_daily_close = getData.get_daily_1factor('close_badj', date_list=trading_day, \
                                              code_list=ZZ800_daily_stock_pool.columns.tolist(), type='stock')
stock_daily_pre_close = getData.get_daily_1factor('pre_close_badj', date_list=trading_day, code_list=\
                                             ZZ800_daily_stock_pool.columns.tolist(), type='stock')
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
stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct < DOWN_ALPHA] = -1 # 不买
stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct > UP_ALPHA] = 1 # 买
NonFactor_alpha_pre2days =  stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct < DOWN_ALPHA].fillna(0) + \
                  stock_daily_alpha_pre2days_rank_pct[stock_daily_alpha_pre2days_rank_pct > UP_ALPHA].fillna(0)

### 获取数据
## 计算RSI指标，参数：N分钟，阈值：0.05-0.95
e1 = time.time()
factor = pd.DataFrame()

for stock in ZZ800_daily_stock_pool.columns.tolist():
    # test
#     stock = ZZ800_daily_stock_pool.columns.tolist()[0]
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
    up_avg = stock_indaydata['pct_chg_1'].shift(1).rolling(MINUTE_ROLLING).sum()
    down_avg = stock_indaydata['pct_chg_0'].shift(1).rolling(MINUTE_ROLLING).sum()
    rs = up_avg / down_avg
    factor_single_stock[stock] = 100 - 100 / (1 + rs)
    factor = pd.concat([factor, factor_single_stock], axis=1)
print(time.time() - e1)

factor2 = copy.deepcopy(factor) # 深复制
del_time = list(filter(lambda x: x < 1000, trade_minutes)) + [1457, 1458, 1459, 1500]

# 把不属于当日个股的因子值变为None,把集合竞价时刻的因子变为None
for date in ZZ800_stock_pool_dict.keys():
    del_stock = list(set(list(factor2.columns)) - set(ZZ800_stock_pool_dict[date]))
    factor2.loc[factor2[del_stock][(factor2.index / 10000).astype(int) == date].index, del_stock] = None
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
new_factor_signal_df[new_factor_signal_df==-2] = -1
new_factor_signal_df = new_factor_signal_df[new_factor_signal_df==1].fillna(0) + \
                        new_factor_signal_df[new_factor_signal_df==-1].fillna(0)

### 临时保存
factor2.to_pickle('/data/group/800319/junkData/temp_factor_by_fc/factor_rsi.pkl')
new_factor_signal_df.to_pickle('/data/group/800319/junkData/temp_factor_by_fc/factor_rsi_signal.pkl')

## 因子测试
e1 = time.time()
temp_factor = FactorBackTest(new_factor_signal_df)
print(time.time()-e1)

e1 = time.time()
temp_factor.evaluation(32)
print(time.time()-e1)

evaluation_result = temp_factor.evaluation_result
temp_factor.result_output('rsi', '/data/group/800319/junkData/temp_factor_by_fc/')