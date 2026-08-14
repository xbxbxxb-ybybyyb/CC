import os
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH = os.path.split(CUR_PATH)[0]
sys.path.append(ROOT_PATH)

import time
import pandas as pd
import datetime as  dt
from day_factor_backtest.AlgoSingleFactorBacktest import *

# 项目映射到个人docker路径


# 回测开始日期
start_date = 20160101

# 回测截至日期
end_date = 20190630

# 因子名称和数据文件
factor_name = 'SampleDayFactor'
factor_data = pd.read_pickle('/data/group/800080/factor_pkl_data/DAY/{}.pkl'.format(factor_name))[factor_name]
factor_data.index = [datetime.datetime.strptime(index, '%Y%m%d') for index in factor_data.index]

# 回测结果路径
result_folder = '/data/group/800080/factor_report/DAY'

t_start = time.time()
instance = AlgoSingleFactorBacktest(start_date, end_date, universe='alpha_universe', holding_period=1,
                                    benchmark='alpha_universe', transaction_cost=0.001, segment_number=10,
                                    seg_by_industry=False, interest_type='', ret_price='vwap', ret_shift=True,
                                    easy_test=False, ic_type='original')

instance.run_backtest(factor_data, name=factor_name, result_folder=result_folder)
print('backtest time cost: ', str(time.time() - t_start))
