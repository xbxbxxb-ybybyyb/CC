import os
import time
import pandas as pd
import sys
import datetime as  dt

# 项目映射到个人docker路径
sys.path.insert(0, '/data/user/015518/day_factor_backtest/')
from AlgoSingleFactorBacktest import *

# 回测开始日期
start_date = 20160101

# 回测截至日期
end_date = 20180701

# 因子名称和数据文件
factor_name = 'gtja_pv105_nis'
factor_data = pd.read_pickle('/data/user/015518/share/factor_data/gtja_pv105_nis.pkl')
factor_data.index = [datetime.datetime.strptime(index, '%Y%m%d') for index in factor_data.index]

# 回测结果路径
result_folder = '/data/user/015518/'

t_start = time.time()
instance = AlgoSingleFactorBacktest(start_date, end_date, universe='alpha_universe', holding_period=1,
                                    benchmark='alpha_universe', transaction_cost=0.001, segment_number=10,
                                    seg_by_industry=False, interest_type='', ret_price='vwap', ret_shift=True,
                                    easy_test=False, ic_type='original')

instance.run_backtest(factor_data, name=factor_name, result_folder=result_folder)
print('backtest time cost: ', str(time.time() - t_start))
