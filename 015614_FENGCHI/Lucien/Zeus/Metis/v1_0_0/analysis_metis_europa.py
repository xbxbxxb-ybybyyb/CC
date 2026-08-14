# coding: utf-8
# Author：fengchi863
# Date ：2023/8/3 13:24

import pandas as pd

from Zeus.Metis.v1_0_0.path_conf import date_config
import json
import os
PERIOD = 'period1'
SUB_VERSION = f'v{PERIOD[-1]}'  # v1 v2 v3
date_dict = date_config[f'{PERIOD}']
pred_type = 'test'
out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
test_out_begin, test_out_end = date_dict[f'test_start_date'], date_dict[f'test_end_date']

pred_data_fpath_list = [
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsv8_pct_XgbRegModel/{out_begin}~{out_end}_fsv8_pct_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsv10_pct_XgbRegModel/{out_begin}~{out_end}_fsv10_pct_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsv11_pct_XgbRegModel/{out_begin}~{out_end}_fsv11_pct_XgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsrs_pct_XgbRegModel/{out_begin}~{out_end}_fsrs_pct_XgbRegModel_{SUB_VERSION}.csv',

    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsv8_pct_LgbRegModel/{out_begin}~{out_end}_fsv8_pct_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsv10_pct_LgbRegModel/{out_begin}~{out_end}_fsv10_pct_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsv11_pct_LgbRegModel/{out_begin}~{out_end}_fsv11_pct_LgbRegModel_{SUB_VERSION}.csv',
    f'/data/user/015614/Zeus/pred/Metis/v1_0_0/fsrs_pct_LgbRegModel/{out_begin}~{out_end}_fsrs_pct_LgbRegModel_{SUB_VERSION}.csv',
]

for idx, pred_data_fpath in enumerate(pred_data_fpath_list):
    pred_data = pd.read_csv(pred_data_fpath, index_col=0)

    # 叠加买入
    if PERIOD == 'period1':
        buy_fpath = f'/data/group/800463/wangj/save_files/Europa_v3/Europa_out_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'
    elif PERIOD == 'period2':
        buy_fpath = f'/data/group/800463/wangj/save_files/Europa_v3/Europa_realout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'
    elif PERIOD == 'period3':
        buy_fpath = f'/data/group/800463/wangj/save_files/Europa_v3/Europa_realrealout_testfit_v3_fac_20230317_maxbeta_final_noroll_merge6models_20230328.csv'

    buy_signal_df = pd.read_csv(buy_fpath, index_col=0).sort_values(['datelist', 'stockID'])
    buy_signal_df['europa_prediction'] = buy_signal_df['vote_sum_pred'] >= 3

    # concat = pd.merge(pred_data, buy_signal_df['europa_prediction'], on='Indexs', how='left')
    concat = pd.merge(pred_data, buy_signal_df['europa_prediction'], on='Indexs')
    """统计第一次没买的，但是第二次买了的"""
    concat.loc[concat.query('europa_prediction == 0 & prediction == 1').index, 'prediction'] = True
    concat.loc[concat.query('europa_prediction == 1 & prediction == 1').index, 'prediction'] = False
    concat.to_csv(os.path.dirname(pred_data_fpath) + '/' + os.path.basename(pred_data_fpath)[:-4] + '_newAdd.csv')


