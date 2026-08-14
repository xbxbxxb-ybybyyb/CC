# coding: utf-8
# Author：fengchi863
# Date ：2023/8/23 16:27

"""
检测提交的模型相关性
"""

import pandas as pd
from Zeus.Europa.v4_0_10.path_conf import date_config

period = 'period1'
pred_type = 'test'
sel_model_names = ['fsv8_pct_AllXgbRegModel', 'fsrs_pct_AllXgbRegModel', 'rffs_pct_AllLgbRegModel',]
date_dict = date_config[period]

out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
valid_path_list = [f'/data/user/015614/Zeus/pred/Europa/v4_0_10/{x}/model/{period}/seed_0/{out_begin}~{out_end}.csv' for x in sel_model_names]

pred_list = list()
for pred_fpath in valid_path_list:
    tmp_pred = pd.read_csv(pred_fpath, index_col=0)['pred_Reg']
    pred_list.append(tmp_pred)

pred_df = pd.concat(pred_list, axis=1)
pred_df.corr(method='spearman')

