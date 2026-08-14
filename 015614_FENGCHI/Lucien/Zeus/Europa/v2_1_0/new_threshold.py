# coding: utf-8
# Author：fengchi863
# Date ：2023/4/1 15:41

import pandas as pd

SUB_VERSION = 'v5'
out_begin = 20220101
out_end = 20220630
pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Europa/v2_1_0/LgbFSV8RegModel/hyper/6/{out_begin}~{out_end}_LgbFSV8RegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/LgbRffsRegModel/hyper/24/{out_begin}~{out_end}_LgbRffsRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/LgbO2ulFSV8RegModel/hyper/36/{out_begin}~{out_end}_LgbO2ulFSV8RegModel_{SUB_VERSION}.csv',

        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/XgbFSV8RegModel/hyper/34/{out_begin}~{out_end}_XgbFSV8RegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/XgbRffsRegModel/hyper/24/{out_begin}~{out_end}_XgbRffsRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/XgbO2ulFSV10RegModel/hyper/7/{out_begin}~{out_end}_XgbO2ulFSV10RegModel_{SUB_VERSION}.csv',

        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/LinRegModel/hyper/0/{out_begin}~{out_end}_LinRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/LinRffsRegModel/hyper/0/{out_begin}~{out_end}_LinRffsRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v2_1_0/LinFsrsRegModel/hyper/0/{out_begin}~{out_end}_LinFsrsRegModel_{SUB_VERSION}.csv',
]

threshold_list = [0.001696, -0.001592, -0.000438,
                  -0.000626, -0.000539, -0.003493,
                  -0.002935, -0.003969, -0.0045]
for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)
    threshold = threshold_list[idx]
    pred_data['prediction'] = pred_data['pred_Reg'] > threshold
    pred_data.to_csv(pred_data_fpath)
