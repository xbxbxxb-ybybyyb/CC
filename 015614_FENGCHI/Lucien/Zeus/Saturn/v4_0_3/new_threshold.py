# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 13:36

import pandas as pd

from Zeus.Saturn.v4_0_3.path_conf import date_config
import json
PERIOD = 'period3'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'test'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/fsv8_XgbRegModel/{out_begin}~{out_end}_fsv8_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/fsv10_XgbRegModel/{out_begin}~{out_end}_fsv10_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/fsv11_XgbRegModel/{out_begin}~{out_end}_fsv11_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/rffs_XgbRegModel/{out_begin}~{out_end}_rffs_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/fsv8_AllXgbRegModel/{out_begin}~{out_end}_fsv8_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/fsv10_AllXgbRegModel/{out_begin}~{out_end}_fsv10_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/fsv11_AllXgbRegModel/{out_begin}~{out_end}_fsv11_AllXgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Saturn/v4_0_3/rffs_AllXgbRegModel/{out_begin}~{out_end}_rffs_AllXgbRegModel_{SUB_VERSION}.csv',
]

threshold_list = [0.014687, 0.014395, 0.014268, 0.018012, 0.012915, 0.012331, 0.012873, 0.013595]
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)

# for idx, pred_path in enumerate(pred_data_fpath_list):
#     with open(pred_path + '_score_threshold.json', 'w') as f:
#         json.dump([threshold_list[idx]], f, ensure_ascii=False, indent=2)
