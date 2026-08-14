# coding: utf-8
# Author：fengchi863
# Date ：2021/3/5 14:56

import os
import pandas as pd
from LimitUpPredStrategy.conf.path_conf import factor_path, samples_path, label_path
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list

factor_names = os.listdir(factor_path)
factor_names = list(map(lambda x: x.split('.')[0], factor_names))

factor_name_list = list(set(factor_name_list).difference(del_factor_list))
factor_df = pd.DataFrame()

for idx, factor in enumerate(factor_name_list):
    tmp_factor = pd.read_pickle(factor_path + factor + '.pkl')
    tmp_factor.name = factor

    # 因子预处理方法
    tmp_factor = tmp_factor.fillna(0)

    if tmp_factor.shape[0] == 1697874:
        factor_df = pd.concat([factor_df, tmp_factor], axis=1)
    else:
        print(factor, tmp_factor.shape)

label = pd.read_pickle(label_path + 'cls_当日收盘是否涨停.pkl')
factor_df.to_pickle(samples_path + 'all_factors.pkl')