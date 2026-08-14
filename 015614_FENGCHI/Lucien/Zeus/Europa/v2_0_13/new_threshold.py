# coding: utf-8
# Author：fengchi863
# Date ：2023/4/1 15:41

import pandas as pd

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/LgbRegModel/20220101~20220630_LgbRegModel_v5.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/LgbRegModelV2/20220101~20220630_LgbRegModelV2_v5.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/LgbRegModelV3/20220101~20220630_LgbRegModelV3_v5.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/XgbRegModel/20220101~20220630_XgbRegModel_v5.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/XgbRegModelV2/20220101~20220630_XgbRegModelV2_v5.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/LinRegModel/20220101~20220630_LinRegModel_v5.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_13/LinRegModelV2/20220101~20220630_LinRegModelV2_v5.csv',
]

threshold_list = [-0.000199, -0.001104, -0.002284, -0.000356, 0.000794, -0.001503, -0.001964]
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)