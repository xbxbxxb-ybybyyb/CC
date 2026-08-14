# coding: utf-8
# Author：fengchi863
# Date ：2021/3/5 14:56

import os
import pandas as pd, numpy as np
from LimitUpPredStrategy.conf.path_conf import factor_path, samples_path, \
    filterd_tick_pool_file_path, factor_std_path
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list

factor_names = os.listdir(factor_std_path)
factor_names = list(map(lambda x: x.split('.')[0], factor_names))

factor_name_list = list(set(factor_names).difference(del_factor_list))
factor_df = pd.DataFrame()

for idx, factor in enumerate(factor_name_list):
    print(factor)
    tmp_factor = pd.read_pickle(factor_std_path + factor + '.pkl')
    print(tmp_factor.shape)
    tmp_factor.name = factor

    factor_df = pd.concat([factor_df, tmp_factor], axis=1)

# 剔除ST\一字板\新股等样本
filterd_tick_pool = pd.read_pickle(filterd_tick_pool_file_path) # 总样本池
filterd_tick_pool = filterd_tick_pool.set_index(['date', 'code', 'tick'])
filterd_tick_pool.index.name = ['date', 'stk_id', 'tick']
# filterd_tick_pool = pd.read_hdf(strategy_pool_file_path, key='virga2consis_board')
factor_df = factor_df.reindex(index=filterd_tick_pool.index)
factor_df.index.names = ['date', 'stk_id', 'time']

factor_df.to_pickle(samples_path + 'all_factors.pkl')