# coding: utf-8
# Author：fengchi863
# Date ：2023/5/15 18:00

import pandas as pd

from Zeus.Saturn.v4_0_6.path_conf import date_config
import json
PERIOD = 'period3'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'test'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv8_AllXgbRegModel/{out_begin}~{out_end}_fsv8_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv10_AllXgbRegModel/{out_begin}~{out_end}_fsv10_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv11_AllXgbRegModel/{out_begin}~{out_end}_fsv11_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/rffs_AllXgbRegModel/{out_begin}~{out_end}_rffs_AllXgbRegModel_{SUB_VERSION}.csv',
]

filtered_samples_pred_test_period1_fpath = f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv8_XgbRegModel/{out_begin}~{out_end}_fsv8_XgbRegModel_{SUB_VERSION}.csv'
filtered_samples_pred_fit_period1_fpath = f'/data/user/015614/Zeus/pred/Saturn/v4_0_6/fsv8_XgbRegModel/{out_begin}~{out_end}_fsv8_XgbRegModel_{SUB_VERSION}.csv'

# test
for pred_data_fpath in pred_data_fpath_list:
    all_samples_index = pd.read_csv(pred_data_fpath, index_col=0).index
    all_samples_pred = pd.read_csv(pred_data_fpath, index_col=0)
    model_name = pred_data_fpath.split('_')[-3] + '_' + pred_data_fpath.split('_')[-2]
    filtered_samples = pd.read_csv(filtered_samples_pred_test_period1_fpath, index_col=0).query(f'{out_begin} <= datelist <= {out_end}')
    ret = all_samples_pred.loc[list(set(filtered_samples.index).intersection(set(all_samples_index)))]
    ret.to_csv('/data/user/015614/Zeus/pred/Saturn/v4_0_6/' + f'duiqi_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')
