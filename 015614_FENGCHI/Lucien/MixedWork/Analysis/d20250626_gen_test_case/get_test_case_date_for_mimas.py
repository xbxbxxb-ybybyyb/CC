# coding: utf-8
# Author：fengchi863
# Date ：2025/7/23 15:41

import pandas as pd
import numpy as np
from dataApi import tradeDate
from tqdm import tqdm

date_list = tradeDate.get_date_range(20250530, 20250729)
# date_list = tradeDate.get_date_range(20250306, 20250710)

for dat in tqdm(date_list):
    # mimas_samples_fpath = f'/data/group/800463/project/project2_prod/daily_data/{dat}_mimas_v1/mimas_factor_v1_{dat}.pkl'
    # mimas_samples_fpath = '/data/group/800463/wangj/model_signal/Mimas/hs1_v1/%s/%s_%s_mimas_fac_20250416_daily_pred_prodmodel.csv' % (dat, dat, dat)
    # p4_samples_fpath = '/data/group/800463/wangj/model_signal/P4/ns1_v1/%s/%s_%s_p4_fac_20250324_daily_pred_prodmodel.csv' % (dat, dat, dat)
    p4_samples_fpath = '/data/group/800463/wangj/model_signal/Saturn/S1_v7/%s/%s_%s_saturn_fac_20241129_daily_pred_prodmodel.csv' % (dat, dat, dat)

    mimas_samples = pd.read_csv(p4_samples_fpath)['vote_sum_pred']
    mimas_signals = (mimas_samples >= 1).sum()
    print(dat, mimas_signals)