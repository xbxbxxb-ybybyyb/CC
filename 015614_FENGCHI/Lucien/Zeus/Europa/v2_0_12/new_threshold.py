# coding: utf-8
# Author：fengchi863
# Date ：2023/4/1 15:41

import pandas as pd

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/LgbRegModel/20210701~20211231_LgbRegModel_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/LgbRegModelV2/20210701~20211231_LgbRegModelV2_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/LgbRegModelV3/20210701~20211231_LgbRegModelV3_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/XgbRegModel/20210701~20211231_XgbRegModel_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/XgbRegModelV2/20210701~20211231_XgbRegModelV2_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/LinRegModel/20210701~20211231_LinRegModel_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/LinRegModelV2/20210701~20211231_LinRegModelV2_v4.csv',
    f'/data/user/015614/Zeus/pred/Europa/v2_0_12/LinRegModelV3/20210701~20211231_LinRegModelV3_v4.csv',
]

threshold_list = [-0.000234, -0.001632, -0.002782, 0.000208, -0.000807, -0.001123, -0.001624, -0.003192]
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)