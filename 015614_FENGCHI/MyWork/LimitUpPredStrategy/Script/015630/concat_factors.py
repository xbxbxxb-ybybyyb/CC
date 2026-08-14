# coding: utf-8
# Author：fengchi863
# Date ：2021/3/5 14:56

import os
import pandas as pd, numpy as np
from LimitUpPredStrategy.conf.path_conf import factor_path, samples_path, \
    filterd_tick_pool_file_path, strategy_pool_file_path, corr_IC_filtered_factor_file_path
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list

# ####读取徐琪筛选出的因子名称####
# filtered_factor = pd.read_excel(corr_IC_filtered_factor_file_path, sheet_name='可使用', index_col=0)
# filtered_factor.index.tolist()

factor_names = os.listdir(factor_path)
factor_names = list(map(lambda x: x.split('.')[0], factor_names))

factor_name_list = list(set(factor_name_list).difference(del_factor_list))
factor_df = pd.DataFrame()

for idx, factor in enumerate(factor_name_list):
    tmp_factor = pd.read_pickle(factor_path + factor + '.pkl')
    tmp_factor.name = factor

    # 因子预处理方法
    tmp_factor = tmp_factor.fillna(0)

    if (tmp_factor.shape[0] == 1697874) or (not np.isinf(tmp_factor).any()):
        factor_df = pd.concat([factor_df, tmp_factor], axis=1)
    else:
        print(factor, tmp_factor.shape, np.isinf(tmp_factor).any())

# 剔除样本
# 剔除ST\一字板\新股等样本
# filterd_tick_pool = pd.read_pickle(filterd_tick_pool_file_path) # 总样本池
stock_pool_dict = {'tx1': 'low_board',
              'xq': 'compensate_board',
              'tx2': 'dragon_board',
              'fn': 'virga2consis_board',
              'all': 'all_strategy_board'}
pool_ = stock_pool_dict['fn']
filterd_tick_pool = pd.read_hdf(strategy_pool_file_path, key=pool_)
factor_df = factor_df.reindex(index=filterd_tick_pool.index)
factor_df.index.names = ['date', 'stk_id', 'time']

factor_df.to_pickle(samples_path + 'zxf_%s.pkl'%pool_)