# coding: utf-8
# Author：fengchi863
# Date ：2022/9/29 13:35

"""
针对目前全样本数据，根据前一日的概念涨停顺序进行筛选，只选择前一天zt_time越靠前的个股
"""

from Zeus.Saturn.v3_0_23.path_conf import saturn_data_test_fpath
import pandas as pd
from LucienUtil import IO

# profit
profit = pd.read_hdf('/data/group/800463/project/project2_prod/profit_backtest/p2_profit_931_0.20_0.10_500_1500.h5')
label = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5')

saturn_sample = pd.read_pickle(saturn_data_test_fpath)
saturn_sample = saturn_sample[['saturn_dt_last_zt_1', 'saturn_Lzt_ZT_Time', 'label_v2o10d1']]
saturn_sample = saturn_sample.join(label[['label_T_close_is_zt']])
saturn_sample['trade_date'] = saturn_sample.index.get_level_values(0)
saturn_sample['trade_date'] = saturn_sample['trade_date'].map(lambda x: int(x.strftime('%Y%m%d')))
saturn_sample['stk_code'] = saturn_sample.index.get_level_values(1)
saturn_sample['last_trade_date'] = saturn_sample['saturn_dt_last_zt_1'].map(lambda x: str(int(x)))
saturn_sample['last_trade_dt'] = saturn_sample['saturn_dt_last_zt_1'].map(lambda x: pd.to_datetime(str(int(x))))
saturn_sample = saturn_sample.set_index(['last_trade_dt', 'stk_code'])
saturn_sample.index.names = ['dt', 'Ticker']

jupiter_sample = IO.read_data([20150101, 20201231], alt='/data/group/800463/fengc/daily/concept/jupiter_concept.h5')
saturn_sample = saturn_sample.join(jupiter_sample)
origin_saturn_sample = saturn_sample.copy()
saturn_sample = saturn_sample.sort_values(['last_trade_date', '概念代码', 'saturn_Lzt_ZT_Time'])
saturn_sample['stk_code'] = saturn_sample.index.get_level_values(1)
saturn_sample = saturn_sample.groupby(['last_trade_date', '概念代码']).agg('first')

#%% 进行样本统计 date20220930
# stats_df = pd.DataFrame(index=['FilterV6.2', '全样本'])
# stats_df.loc['FilterV6.2', '样本个数'] = len(saturn_sample)
# stats_df.loc['FilterV6.2', '整体胜率'] = (saturn_sample['label_v2o10d1'] > 0).sum() / len(saturn_sample)
# stats_df.loc['FilterV6.2', '收益率均值'] = saturn_sample['label_v2o10d1'].mean()
# stats_df.loc['FilterV6.2', '中位数'] = saturn_sample['label_v2o10d1'].median()
# stats_df.loc['FilterV6.2', 'std'] = saturn_sample['label_v2o10d1'].std()
# stats_df.loc['FilterV6.2', 'T日收盘涨停比例'] = saturn_sample['label_T_close_is_zt'].sum() / len(saturn_sample)
#
# stats_df.loc['全样本', '样本个数'] = len(origin_saturn_sample)
# stats_df.loc['全样本', '整体胜率'] = (origin_saturn_sample['label_v2o10d1'] > 0).sum() / len(origin_saturn_sample)
# stats_df.loc['全样本', '收益率均值'] = origin_saturn_sample['label_v2o10d1'].mean()
# stats_df.loc['全样本', '中位数'] = origin_saturn_sample['label_v2o10d1'].median()
# stats_df.loc['全样本', 'std'] = origin_saturn_sample['label_v2o10d1'].std()
# stats_df.loc['全样本', 'T日收盘涨停比例'] = origin_saturn_sample['label_T_close_is_zt'].sum() / len(origin_saturn_sample)
#
# stats_df = stats_df.T
# from dataApi.sendInfo import send_file
# send_file(stats_df)

#%% 进行样本筛选，生成数据集，date20221020
# 全样本
saturn_sample['trade_date'] = saturn_sample['trade_date'].map(lambda x: pd.to_datetime(str(x)))
saturn_sample = saturn_sample.set_index(['trade_date', 'stk_code'])
saturn_sample = saturn_sample.sort_values(['trade_date', 'stk_code'])
saturn_sample.index.names = ['dt', 'Ticker']
import os
group_path = '/data/group/800463/'
saturn_data_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_20220927/V6_20220927_3period/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_931_20160101_20201231.pkl')
saturn_data = pd.read_pickle(saturn_data_test_fpath)
saturn_data = saturn_data.reindex(index=saturn_sample.index)
os.makedirs(group_path + 'fengc/for_xly/saturn/V6_20220927/V6_20220927_3period/', exist_ok=True)
pd.to_pickle(saturn_data, group_path + 'fengc/for_xly/saturn/V6_20220927/V6_20220927_3period/factor_df_filter_v6_2_931_20160101_20201231.pkl')

saturn_data_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_20220927/V6_20220927_1period/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_931_20160101_20201231.pkl')
saturn_data = pd.read_pickle(saturn_data_test_fpath)
saturn_data = saturn_data.reindex(index=saturn_sample.index)
os.makedirs(group_path + 'fengc/for_xly/saturn/V6_20220927/V6_20220927_1period/', exist_ok=True)
pd.to_pickle(saturn_data, group_path + 'fengc/for_xly/saturn/V6_20220927/V6_20220927_1period/factor_df_filter_v6_2_931_20160101_20201231.pkl')

saturn_data_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_20220927/V6_20220927_6period/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_931_20160101_20201231.pkl')
saturn_data = pd.read_pickle(saturn_data_test_fpath)
saturn_data = saturn_data.reindex(index=saturn_sample.index)
os.makedirs(group_path + 'fengc/for_xly/saturn/V6_20220927/V6_20220927_6period/', exist_ok=True)
pd.to_pickle(saturn_data, group_path + 'fengc/for_xly/saturn/V6_20220927/V6_20220927_6period/factor_df_filter_v6_2_931_20160101_20201231.pkl')