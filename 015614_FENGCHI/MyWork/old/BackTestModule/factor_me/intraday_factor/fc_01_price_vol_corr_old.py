import pandas as pd, numpy as np
import os

from QuickFactorEvaluationBackTest import FactorBackTest
from config import ZZ800_daily_stock_pool
from dataApi import getData, stockList, tradeDate
from dataApi.tradeDate import trade_minutes
import time
import copy

start = 20170101
end = 20191231
e1 = time.time()
## 获取ZZ500股票池
# stock_pool = stock_pool=pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5','ZZ500')
ZZ800_daily_stock_pool = pd.DataFrame(ZZ800_daily_stock_pool).stack().reset_index()
ZZ800_daily_stock_pool['level_0'] = True
ZZ800_daily_stock_pool = ZZ800_daily_stock_pool.pivot('level_1', 0, 'level_0').fillna(False)
ZZ800_daily_stock_pool = ZZ800_daily_stock_pool[(ZZ800_daily_stock_pool.index >= start) * (ZZ800_daily_stock_pool.index <= end)]
ZZ800_daily_stock_pool = ZZ800_daily_stock_pool.drop(ZZ800_daily_stock_pool.loc[:,ZZ800_daily_stock_pool.\
                                                                                sum(axis=0)==0].columns.tolist(),axis=1)
ZZ800_stock_pool_dict = {int(i): ZZ800_daily_stock_pool.loc[i][ZZ800_daily_stock_pool.loc[i,:]==True].index.tolist() \
                   for i in ZZ800_daily_stock_pool.index}
trading_day = tradeDate.get_date_range(start, end, period='D')

## 构建因子
factor = pd.DataFrame()
for stock in ZZ800_daily_stock_pool.columns.tolist():
    # test
#     stock = stock_pool.columns.tolist()[0]
    print(stockList.trans_int2windcode(stock))
    f = pd.HDFStore('/data/group/800319/junkData/minuteByStock/' + str(stock) + '.h5', 'r')
    stock_indaydata = f[f.keys()[0]][(f[f.keys()[0]]['date'] >= start) * (f[f.keys()[0]]['date'] <= end)]
    stock_indaydata['datetime'] = stock_indaydata['date'] * 10000 + stock_indaydata['time']
    stock_indaydata = stock_indaydata.set_index('datetime').drop(['date', 'time'], axis=1)
    ## 建立个股的因子值
    factor_single_stock = pd.DataFrame(index=stock_indaydata.index, columns=[stock])
    factor_single_stock[stock] = stock_indaydata['close'].shift(1).rolling(30).corr(stock_indaydata['vol'].shift(1))
    factor = pd.concat([factor, factor_single_stock], axis=1)

factor2 = copy.deepcopy(factor)
del_time = list(filter(lambda x: x < 1000, trade_minutes)) + [1457, 1458, 1459, 1500]

# 把不属于当日个股的因子值变为0,把集合竞价时刻的因子变为0
for date in ZZ800_stock_pool_dict.keys():
    del_stock = list(set(list(factor2.columns)) - set(ZZ800_stock_pool_dict[date]))
    factor2.loc[factor2[del_stock][(factor2.index / 10000).astype(int) == date].index, del_stock] = None
factor2[(factor2.index % 10000).isin(del_time)] = None

factor_signal = factor2.rank(ascending=False, axis=1, pct=True)
factor_signal[factor_signal > 0.95] = 1
factor_signal[factor_signal < 0.05] = -1

factor_signal_df = factor_signal[factor_signal > 0.95].fillna(0) + \
                    factor_signal[factor_signal < 0.05].fillna(0)

## 因子回测
factor_signal_df = pd.read_pickle('/data/group/800319/junkData/'+\
                                  'temp_factor_by_fc/factor_pv_signal.pkl')
e1 = time.time()
temp_factor = FactorBackTest(factor_signal_df)
print(time.time()-e1)

e1 = time.time()
temp_factor.evaluation(32)
print(time.time()-e1)