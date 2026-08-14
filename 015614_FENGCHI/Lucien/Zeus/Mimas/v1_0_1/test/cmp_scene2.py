# coding: utf-8
# Author：fengchi863
# Date ：2024/6/19 11:12

"""
在对齐后的样本上进行参与率的划分
"""

import pandas as pd
import numpy as np
from Zeus.Europa.v1_0_1.path_conf import *
import os

scene_samples_fpath = '/data/group/800463/sunss/europa/20240531_scene/factor_df_draw_20160101_20221130.pkl'

scene_df = pd.read_pickle(scene_samples_fpath)

model_name_list = os.listdir('/data/user/015614/Zeus/pred/Europa/v1_0_1/')

period_list = ['period1', 'period2', 'period3', 'period4']

# 转换格式
scene_df['stockID'] = scene_df.index.get_level_values(1).tolist()
scene_df['datelist'] = scene_df.index.get_level_values(0).map(lambda x: x.strftime("%Y%m%d"))
scene_df['Indexs'] = scene_df[['stockID', 'datelist']].apply(lambda x: x['stockID'] + ' ' + x['datelist'], axis=1)
scene_df = scene_df.set_index('Indexs', drop=True)
scene_df_index = scene_df.index.tolist()

for model_name in model_name_list:
    csv_fpath_list = os.listdir(f'/data/user/015614/Zeus/pred/Europa/v1_0_1/{model_name}/')
    for period in period_list:
        test_start_date, test_end_date, fit_start_date, fit_end_date = date_config[period]['test_start_date'], date_config[period]['test_end_date'], date_config[period]['fit_start_date'], date_config[period]['fit_end_date']
        csv_df = pd.read_csv(f'/data/user/015614/Zeus/pred/Europa/v1_0_1/{model_name}/{test_start_date}~{test_end_date}.csv', index_col=0)
        new_csv_df = csv_df.loc[list(set(csv_df.index.tolist()).intersection(scene_df_index))]
        new_threshold = np.percentile(new_csv_df['pred_Reg'].values, 60)
        os.makedirs(f'/data/user/015614/Zeus/pred/Europa/v1_0_1_scene/{model_name}', exist_ok=True)
        new_csv_df['prediction'] = new_csv_df['pred_Reg'] >= new_threshold
        new_csv_df.to_csv(f'/data/user/015614/Zeus/pred/Europa/v1_0_1_scene/{model_name}/{test_start_date}~{test_end_date}.csv')

        csv_df = pd.read_csv(f'/data/user/015614/Zeus/pred/Europa/v1_0_1/{model_name}/{fit_start_date}~{fit_end_date}.csv', index_col=0)
        new_csv_df = csv_df.loc[list(set(csv_df.index.tolist()).intersection(scene_df_index))]
        new_csv_df['prediction'] = new_csv_df['pred_Reg'] >= new_threshold
        new_csv_df.to_csv(f'/data/user/015614/Zeus/pred/Europa/v1_0_1_scene/{model_name}/{fit_start_date}~{fit_end_date}.csv')

