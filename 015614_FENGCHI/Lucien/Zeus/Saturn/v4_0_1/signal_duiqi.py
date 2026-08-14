# coding: utf-8
# Author：fengchi863
# Date ：2023/5/15 18:00

import pandas as pd

from Zeus.Saturn.v4_0_1.path_conf import date_config
import json
PERIOD = 'period1'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'fit'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/fsv8_LgbRegModel/{out_begin}~{out_end}_fsv8_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/fsv10_LgbRegModel/{out_begin}~{out_end}_fsv10_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/fsv11_LgbRegModel/{out_begin}~{out_end}_fsv11_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/rffs_LgbRegModel/{out_begin}~{out_end}_rffs_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/fsv8_XgbRegModel/{out_begin}~{out_end}_fsv8_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/fsv10_XgbRegModel/{out_begin}~{out_end}_fsv10_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/fsv11_XgbRegModel/{out_begin}~{out_end}_fsv11_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_1/rffs_XgbRegModel/{out_begin}~{out_end}_rffs_XgbRegModel_{SUB_VERSION}.csv',
]

all_samples_pred_test_period1_fpath = '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20200630_lgbRegModel_v1.csv'
all_samples_pred_fit_period1_fpath = '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_21/20190102~20201231_lgbRegModel_v1.csv'

# test
# for pred_data_fpath in pred_data_fpath_list:
#     filtered_samples_index = pd.read_csv(pred_data_fpath, index_col=0).index
#     model_name = pred_data_fpath.split('_')[-3] + '_' + pred_data_fpath.split('_')[-2]
#     test_samples = pd.read_csv(all_samples_pred_test_period1_fpath, index_col=0).query(f'{out_begin} <= datelist <= {out_end}')
#     ret = test_samples.loc[list(set(test_samples.index).intersection(set(filtered_samples_index)))]
#     ret.to_csv('/data/user/015614/Zeus/pred/Saturn/v4_0_1/' + f'duiqi_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')

# fit
for pred_data_fpath in pred_data_fpath_list:
    filtered_samples_index = pd.read_csv(pred_data_fpath, index_col=0).index
    filtered_samples = pd.read_csv(pred_data_fpath, index_col=0)
    model_name = pred_data_fpath.split('_')[-3] + '_' + pred_data_fpath.split('_')[-2]
    test_samples = pd.read_csv(all_samples_pred_test_period1_fpath, index_col=0).query(f'{out_begin} <= datelist <= {out_end}')
    fit_samples = pd.read_csv(all_samples_pred_fit_period1_fpath, index_col=0).query(f'{out_begin} <= datelist <= {out_end}')
    fit_samples = pd.concat([test_samples, fit_samples], axis=0).drop_duplicates(subset=['stockID', 'datelist'], keep='first')
    ret = fit_samples.loc[list(set(fit_samples.index).intersection(set(filtered_samples_index)))].sort_values('datelist')
    ret.to_csv('/data/user/015614/Zeus/pred/Saturn/v4_0_1/' + f'duiqi_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')