# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 13:36

import pandas as pd

from Zeus.JupiterZ.v1_0_3.path_conf import date_config
import json
PERIOD = 'period5'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'test'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/{out_begin}~{out_end}_rffs_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/{out_begin}~{out_end}_fsv8_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/{out_begin}~{out_end}_fsv11_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/{out_begin}~{out_end}_rffs_afterZ_lowCost_XgbRegModel_{SUB_VERSION}.csv',
]

# pred_model_fpath_list = [
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/fsv10_lowCost_LgbRegModel/',
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/fsv8_afterZ_lowCost_LgbRegModel/',
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/fsv11_lowCost_XgbRegModel/',
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/fsv8_afterZ_lowCost_XgbRegModel/',
# ]

pred_model_fpath_list = [
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/rffs_lowCost_LgbRegModel/',
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/fsv8_afterZ_lowCost_LgbRegModel/',
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/fsv11_afterZ_lowCost_LgbRegModel/',
    f'/data/user/015614/shared/for_wj/20230427_JupiterZ_V20230415_period5/rffs_afterZ_lowCost_XgbRegModel/',
]


# pred_model_fpath_list = [
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/{out_begin}~{out_end}_fsv10_lowCost_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/{out_begin}~{out_end}_fsv8_afterZ_lowCost_LgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/{out_begin}~{out_end}_fsv11_lowCost_XgbRegModel_{SUB_VERSION}.csv',
#     f'/data/user/015614/shared/for_wj/20230426_JupiterZ_V20230415_period4/{out_begin}~{out_end}_fsv8_afterZ_lowCost_XgbRegModel_{SUB_VERSION}.csv',
# ]

# threshold_list = [0.004003, 0.004614, 0.005963, 0.006354] # 1 test
# threshold_list = [0.00671, 0.006481, 0.006956, 0.007761] 1 fit
# threshold_list = [0.005487, 0.006183, 0.008206, 0.006922] # 2 test
# threshold_list = [0.002028, 0.002067, 0.001606, 0.001117] 2 fit
# threshold_list = [0.002109, 0.000622, -0.000155, -0.000454] # 3 test fit
# threshold_list = [0.004539, 0.006825, 0.007982, 0.011504] # 4 test
threshold_list = [0.003029, 0.006602, 0.006322, 0.009639]
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)

for idx, pred_path in enumerate(pred_model_fpath_list):
    with open(pred_path + '_score_threshold.json', 'w') as f:
        json.dump([threshold_list[idx]], f, ensure_ascii=False, indent=2)
