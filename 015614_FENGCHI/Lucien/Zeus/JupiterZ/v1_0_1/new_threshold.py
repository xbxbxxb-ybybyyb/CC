# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 13:36

import pandas as pd

from Zeus.JupiterZ.v1_0_1.path_conf import date_config
PERIOD = 'period1'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'fit'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/shared/for_wj/20230424_JupiterZ_V20230415_period123/rffs_lowCost_LgbRegModel/{out_begin}~{out_end}_rffs_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/shared/for_wj/20230424_JupiterZ_V20230415_period123/fsv8_lowCost_LgbRegModel/{out_begin}~{out_end}_fsv8_lowCost_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/shared/for_wj/20230424_JupiterZ_V20230415_period123/rffs_all_LgbRegModel/{out_begin}~{out_end}_rffs_all_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/shared/for_wj/20230424_JupiterZ_V20230415_period123/fsv11_all_LgbRegModel/{out_begin}~{out_end}_fsv11_all_LgbRegModel_{SUB_VERSION}.csv',
]

threshold_list = [0.004003, 0.004614, 0.005963, 0.006354] # 1 test
# threshold_list = [0.00671, 0.006481, 0.006956, 0.007761] 1 fit
# threshold_list = [0.005487, 0.006183, 0.008206, 0.006922] # 2 test
# threshold_list = [0.002028, 0.002067, 0.001606, 0.001117] 2 fit
# threshold_list = [0.002109, 0.000622, -0.000155, -0.000454] # 3 test fit
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)