import pandas as pd
import numpy as np
import os

# os.chdir('/data/group/800319/BackTestModule/')
from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time


start = 20190101
end = 20191231
e1 = time.time()

#定义股票池
stock_pool = get_index_comp(start,end,'ZZ500')

trading_day = s.tradingday(start, end, \
                           frequency='DAY', dayType=None, dateType='TRADINGDAYS')
trading_day = list(map(int, trading_day))

#定义因子信号
factor_df = pd.DataFrame()
for stk in stock_pool[20190102]:
    temp_minutest_data = load_minutes_data(stk, trading_day)

    temp_minutest_data['MA_signal'] = temp_minutest_data['close'].rolling(10).mean() - temp_minutest_data['close'].rolling(30).mean()
    temp_minutest_data['break'] = temp_minutest_data['MA_signal'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).rolling(2).sum()
    temp_minutest_data['break'] = temp_minutest_data['break'].eq(0) * 1
    temp_minutest_data['break_sinal'] = temp_minutest_data['break'] * temp_minutest_data['MA_signal'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    factor_df[stk] = temp_minutest_data['break_sinal']
    if len(factor_df.columns) >= 50:
        break
del temp_minutest_data
print(time.time() - e1)
e1 = time.time()

#定义因子回测对象，输入开始日期、结束日期、股票池(dict)、基准指数、因子信号DataFrame作为初始化参数
factor_test = FactorBackTest(factor_df)
print(time.time()-e1)
del factor_df
#并行回测
factor_test.evaluation(5)
print(factor_test.evaluation_result)
print(1)