# coding: utf-8
# Author：fengchi863
# Date ：2023/3/20 19:24

"""
样本对齐
"""

import pandas as pd
from Zeus.Europa.v2_0_9.path_conf import data_test_fpath_with_label

new_samples = pd.read_pickle(data_test_fpath_with_label)

old_model_period1_test_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20191001~20200331_LgbRegModelV3_v1.csv'
old_model_period1_fit_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20200401~20201231_LgbRegModelV3_v1.csv'
old_model_period2_test_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20200401~20200930_LgbRegModelV3_v2.csv'
old_model_period2_fit_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20201001~20210630_LgbRegModelV3_v2.csv'
old_model_period3_test_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20201001~20210331_LgbRegModelV3_v3.csv'
old_model_period3_fit_fpath = '/data/user/015614/Zeus/pred/Europa/v2_0_4/LgbRegModelV3/20210401~20211231_LgbRegModelV3_v3.csv'

def trans_signal_index(df):
    _df = df.copy()
    _df['dt'] = _df['datelist'].apply(lambda x: pd.to_datetime(str(x)))
    _df = _df.reset_index().set_index(['dt', 'stockID'])
    _df.index.names = ['dt', 'Ticker']
    return _df

for fpath in [old_model_period1_test_fpath, old_model_period1_fit_fpath,
              old_model_period2_test_fpath, old_model_period2_fit_fpath,
              old_model_period3_test_fpath, old_model_period3_fit_fpath]:
    pred = pd.read_csv(fpath, index_col=0)
    pred_ = trans_signal_index(pred)
    new_index = list(set(pred_.index).intersection(set(new_samples.index)))
    new_pred = pred_.loc[new_index]
    new_pred = new_pred.set_index('Indexs')
    new_pred.to_csv(fpath[:-4] + '_duiqi_v209' + '.csv')
