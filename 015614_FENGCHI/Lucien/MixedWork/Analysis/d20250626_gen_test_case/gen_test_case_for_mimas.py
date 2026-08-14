# coding: utf-8
# Author：fengchi863
# Date ：2025/7/16 10:01


import pandas as pd
import numpy as np
from dataApi import tradeDate
from tqdm import tqdm

date_list = tradeDate.get_date_range(20241001, 20250710)
# date_list = tradeDate.get_date_range(20250306, 20250710)

for dat in tqdm(date_list):
    mimas_samples_fpath = f'/data/group/800463/project/project2_prod/daily_data/{dat}_mimas_v1/mimas_factor_v1_{dat}.pkl'
    mimas_morning_fpath = f'/data/group/800463/project/project2_prod/daily_data/{dat}_mimas_v1/mimas_factor_v1_{dat}.pkl'

    mimas_samples = pd.read_pickle(mimas_samples_fpath)
    mimas_morning = pd.read_pickle(mimas_morning_fpath)
    mimas_samples = mimas_samples[['Next_day_first_ZT_Time', 'Next_day_first_DT_Time']]
    mimas_morning['not_in_mimas_samples'] = mimas_morning.index.map(lambda x: x not in mimas_samples.index)

    mimas_morning['Next_day_first_ZT_Time'] = mimas_morning.index.map(lambda x: mimas_samples.loc[x, 'Next_day_first_ZT_Time'] if x in mimas_samples.index else '无')
    mimas_morning['Next_day_first_DT_Time'] = mimas_morning.index.map(lambda x: mimas_samples.loc[x, 'Next_day_first_DT_Time'] if x in mimas_samples.index else '无')

    mimas_morning = mimas_morning[['Next_day_first_ZT_Time', 'Next_day_first_DT_Time', 'not_in_mimas_samples']]

    if mimas_morning['Next_day_first_DT_Time'].sum() > 0:
        print(dat)