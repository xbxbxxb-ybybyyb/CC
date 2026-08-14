# coding: utf-8
# Author：fengchi863
# Date ：2023/4/12 10:33

import pandas as pd

v2_period5_pred = pd.read_csv('/data/user/015614/Zeus/pred/Europa/v1_0_32/LgbRegModel/20220101~20220630_LgbRegModel_v5.csv', index_col=0)
v2v3_period5_pred = pd.read_csv('/data/user/015614/Zeus/pred/Europa/v1_0_32/LgbRegModelV2V3duiqi/20220101~20220630_LgbRegModelV2V3duiqi_v5.csv', index_col=0)

v2_duiqi_period5_pred = v2_period5_pred.loc[v2v3_period5_pred.index]
v2_duiqi_period5_pred = v2_duiqi_period5_pred.drop_duplicates()
v2_duiqi_period5_pred.to_csv('/data/user/015614/Zeus/pred/Europa/v1_0_32/LgbRegModel/20220101~20220630_LgbRegModel_v5_duiqi.csv')

v2v3_period5_pred = v2v3_period5_pred.drop_duplicates()
v2v3_period5_pred.to_csv('/data/user/015614/Zeus/pred/Europa/v1_0_32/LgbRegModelV2V3duiqi/20220101~20220630_LgbRegModelV2V3duiqi_v5.csv')