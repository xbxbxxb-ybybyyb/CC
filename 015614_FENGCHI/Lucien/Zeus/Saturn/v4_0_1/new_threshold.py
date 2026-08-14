# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 13:36

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

# pred_data_fpath_list = [
#     f'/data/user/015614/shared/for_wj/20230424_Saturn_V20230415_period123/rffs_lowCost_LgbRegModel/{out_begin}~{out_end}_rffs_lowCost_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230424_Saturn_V20230415_period123/fsv8_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv8_lowCost_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230424_Saturn_V20230415_period123/rffs_all_LgbRegModel/{out_begin}~{out_end}_rffs_all_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230424_Saturn_V20230415_period123/fsv11_all_LgbRegModel/{out_begin}~{out_end}_fsv11_all_LgbRegModel_{SUB_VERSION}.csv',
# ]

# pred_data_fpath_list = [
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/fsv10_lowCost_LgbRegModel/',
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/fsv8_afterZ_lowCost_LgbRegModel/',
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/fsv11_lowCost_XgbRegModel/',
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/fsv8_afterZ_lowCost_XgbRegModel/',
# ]

# pred_data_fpath_list = [
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/{out_begin}~{out_end}_fsv10_lowCost_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/{out_begin}~{out_end}_fsv8_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/{out_begin}~{out_end}_fsv11_lowCost_XgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230426_Saturn_V20230415_period4/{out_begin}~{out_end}_fsv8_afterZ_lowCost_XgbRegModel_{SUB_VERSION}.csv',
# ]

threshold_list = [-0.000433, 0.000933, 0.000116, 0.00122,
                  0.005728, 0.005738, 0.004974, 0.009187]
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)

# for idx, pred_path in enumerate(pred_data_fpath_list):
#     with open(pred_path + '_score_threshold.json', 'w') as f:
#         json.dump([threshold_list[idx]], f, ensure_ascii=False, indent=2)
