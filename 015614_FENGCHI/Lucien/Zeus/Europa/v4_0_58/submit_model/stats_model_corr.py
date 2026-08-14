# coding: utf-8
# Author：fengchi863
# Date ：2023/8/23 16:27

"""
检测提交的模型相关性
"""

import pandas as pd
from itertools import product
from Zeus.Europa.v4_0_58.path_conf import date_config

period = 'period6'
pred_type = 'test'

date_dict = date_config[period]

version_list = ['v4_0_57', 'v4_0_58']
factor_select_list = ['fsv8', 'fsv10', 'fsv11', 'fsrs']
scaler_list = ['scaler1', 'scaler2']
model_list = ['AllXgbRegModel', 'AllLgbRegModel']

product_list = list(product(version_list, factor_select_list, scaler_list, model_list))
product_list = [ ('v4_0_58', 'fsrs', 'scaler1', 'AllXgbRegModel'),
                 ('v4_0_58', 'fsv11', 'scaler1', 'AllXgbRegModel'),
                 ('v4_0_57', 'fsv10', 'scaler1', 'AllLgbRegModel')]
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']

valid_path_list = [f'/data/user/015614/Zeus/pred/Europa/{pro[0]}/{pro[1]}_{pro[2]}_pct_{pro[3]}/model/{period}/seed_0/{out_begin}~{out_end}.csv' for pro in product_list]

pred_list = list()
for pred_fpath in valid_path_list:
    tmp_pred = pd.read_csv(pred_fpath, index_col=0)['pred_Reg']
    pred_list.append(tmp_pred)

pred_df = pd.concat(pred_list, axis=1)
pred_df.columns = product_list
corr_check = pred_df.corr(method='spearman')
print(corr_check)
corr_check.to_excel('/data/user/015614/junkData/相关性.xlsx')

