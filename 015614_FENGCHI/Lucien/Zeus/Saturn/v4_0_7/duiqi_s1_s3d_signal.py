# coding: utf-8
# Author：fengchi863
# Date ：2023/6/14 19:52

import pandas as pd

from Zeus.Saturn.v4_0_7.path_conf import date_config
import json
PERIOD = 'period3'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'fit'
s3d_attend_pct = 40
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_7/fsv8_AllXgbRegModel/{out_begin}~{out_end}_fsv8_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_7/fsv10_AllXgbRegModel/{out_begin}~{out_end}_fsv10_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_7/fsv11_AllXgbRegModel/{out_begin}~{out_end}_fsv11_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_7/rffs_AllXgbRegModel/{out_begin}~{out_end}_rffs_AllXgbRegModel_{SUB_VERSION}.csv',
]

s1_3d_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_9/attend{s3d_attend_pct}pct/fsv8_AllXgbRegModel/{out_begin}~{out_end}_fsv8_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_9/attend{s3d_attend_pct}pct/fsv10_AllXgbRegModel/{out_begin}~{out_end}_fsv10_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_9/attend{s3d_attend_pct}pct/fsv11_AllXgbRegModel/{out_begin}~{out_end}_fsv11_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_9/attend{s3d_attend_pct}pct/rffs_AllXgbRegModel/{out_begin}~{out_end}_rffs_AllXgbRegModel_{SUB_VERSION}.csv'
]

# test
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    all_samples_index = pd.read_csv(pred_data_fpath, index_col=0).index
    all_samples_pred = pd.read_csv(pred_data_fpath, index_col=0)
    model_name = pred_data_fpath.split('_')[-3] + '_' + pred_data_fpath.split('_')[-2]

    s1_3d_data_fpath = s1_3d_data_fpath_list[idx]
    s1_3d_samples = pd.read_csv(s1_3d_data_fpath, index_col=0).query(f'{out_begin} <= datelist <= {out_end}')
    all1_jiaoji_index = list(set(s1_3d_samples.query('prediction == 1').index).intersection(set(all_samples_pred.query('prediction == 1').index)))
    not1_index = list(set(all_samples_pred.index).difference(set(all1_jiaoji_index)))
    all_samples_pred.loc[not1_index, 'prediction'] = False

    s1_s3d_all_index = list(set(s1_3d_samples.index).intersection(set(all_samples_index)))
    all_samples_pred.loc[s1_s3d_all_index, 's3d_prediction'] = s1_3d_samples.loc[s1_s3d_all_index, 'prediction']    # 回测时根据S3的信号把 S3==False 成交量设置为0
    all_samples_pred['s3d_prediction'] = all_samples_pred['s3d_prediction'].fillna(False)
    all_samples_pred.to_csv('/data/user/015614/Zeus/pred/Saturn/v4_0_7/' + f'attend{s3d_attend_pct}_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')
    print(f'saved in attend{s3d_attend_pct}_{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv')