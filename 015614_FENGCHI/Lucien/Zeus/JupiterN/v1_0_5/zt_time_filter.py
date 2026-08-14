# coding: utf-8
# Author：fengchi863
# Date ：2023/2/1 21:20

import pandas as pd
from LucienUtil.FileUtil import FileUtil

def transform_zt_time(pred_df):
    pred_df['dt'] = pred_df['datelist'].apply(lambda x: pd.to_datetime(str(x)))
    pred_df['Ticker'] = pred_df['stockID']
    pred_df['Indexs'] = pred_df.index.tolist()
    pred_df = pred_df.set_index(['dt', 'stockID'], drop=False)
    label = pd.read_pickle('/data/group/800463/sunss/jupiter/20221220/factor_df_all_20160101_20220630.pkl')
    # label = label.query('ZT_Time <= 100000000')
    # label = label.query('ZT_Time > 100000000')
    label = label.query('ZT_Time <= 93500000')
    # label = label.query('ZT_Time > 93500000')
    pred_df = pred_df.loc[list(set(pred_df.index).intersection(set(label.index)))]
    pred_df = pred_df.sort_values(['datelist', 'Ticker'])
    pred_df = pred_df.set_index('Indexs')
    return pred_df

valid_path_list = [
    f'/data/user/015614/Zeus/pred/JupiterN/v1_0_5/LgbRegModel/20191001~20200331_LgbRegModel_v1.csv',
    f'/data/user/015614/Zeus/pred/JupiterN/v1_0_5/LgbRegModel/20200401~20201231_LgbRegModel_v1.csv',
    f'/data/user/015614/Zeus/pred/JupiterN/v1_0_5/LgbRegModel/20200401~20200930_LgbRegModel_v2.csv',
    f'/data/user/015614/Zeus/pred/JupiterN/v1_0_5/LgbRegModel/20201001~20210630_LgbRegModel_v2.csv',
]

for fpath in valid_path_list:
    check = pd.read_csv(fpath, index_col=0)
    zt_filtered_check = transform_zt_time(check)
    # fpath = fpath[:-4] + '_before10' + fpath[-4:]
    # fpath = fpath[:-4] + '_after10' + fpath[-4:]
    fpath = fpath[:-4] + '_before935' + fpath[-4:]
    # fpath = fpath[:-4] + '_after935' + fpath[-4:]
    zt_filtered_check.to_csv(fpath)