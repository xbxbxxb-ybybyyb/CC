# coding: utf-8
# Author：fengchi863
# Date ：2023/7/14 13:24

"""
半小时的因子数据和因子列表、因子筛选文件。其中因子数据中包含s_xx列，分别为1000、1030、1100三个时点；label_diff_pct为当前时点开始快速卖出的收益率-剩余时间均匀卖出的收益率-0.1%
这是半小时的模拟收益文件，其中buy_vol,buy_amt为前日europa模拟买入量、买入额；pct_v2为v2卖出模拟收益率-0.2%;pct_v1为时点s_xx后快速卖出的模拟收益率-0.3%；pct_diff=pct_v1-pct_v2。需要注意收益率均已扣费。
"""

from Zeus.Saturn.v6_0_3.config.path_conf import *
import pandas as pd
import numpy as np
import datetime as dt
import importlib
from Zeus.Saturn.v6_0_3.config.strat_conf import *

data_fpath = '/data/group/800463/sunss/saturn/20241129/factor_df_s1_20160101_20210630.pkl'

data_df = pd.read_pickle(data_fpath)

print(1)

data_df['stock_code'] = data_df.index.get_level_values(1).tolist()
data_df['is_bjs'] = data_df['stock_code'].apply(lambda x: str(x).endswith('BJ'))
data_df['is_kcb'] = data_df['stock_code'].apply(lambda x: str(x).startswith('68'))
data_df['is_cyb'] = data_df['stock_code'].apply(lambda x: str(x).startswith('3'))

data_df['datelist'] = data_df.index.get_level_values(0).map(lambda x: pd.to_datetime(x).strftime('%Y%m%d')).map(int)

period_list = ['period1', 'period2', 'period3', 'period4', 'period5', 'period6']
stats_df = pd.DataFrame(index=period_list, columns=['bjs_num', 'kcb_num', 'cyb_num', 'sample_num'])
for period in period_list:
    module_name = f'Zeus.Saturn.v6_0_3.config.path_conf'
    module = importlib.import_module(module_name)

    test_start_date, test_end_date = DATE_CONFIG[period]['test_start_date'], DATE_CONFIG[period]['test_end_date']
    fit_start_date, fit_end_date = DATE_CONFIG[period]['fit_start_date'], DATE_CONFIG[period]['fit_end_date']

    bjs_num = data_df.query(f'{test_start_date} <= datelist <= {test_end_date}')['is_bjs'].sum()
    kcb_num = data_df.query(f'{test_start_date} <= datelist <= {test_end_date}')['is_kcb'].sum()
    cyb_num = data_df.query(f'{test_start_date} <= datelist <= {test_end_date}')['is_cyb'].sum()
    sample_num = data_df.query(f'{test_start_date} <= datelist <= {test_end_date}').shape[0]

    stats_df.loc[period, 'bjs_num'] = bjs_num
    stats_df.loc[period, 'kcb_num'] = kcb_num
    stats_df.loc[period, 'cyb_num'] = bjs_num
    stats_df.loc[period, 'sample_num'] = sample_num

print(1)



