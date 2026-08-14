# coding: utf-8
# Author：fengchi863
# Date ：2024/3/22 10:50

import pandas as pd
import numpy as np
from dataApi import tradeDate
from tqdm import tqdm

root_path = '/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/daily_Wind&SW/'
basic_sample = pd.read_pickle('/data/group/800463/sunss/saturn/20230626/factor_df_931_20160101_20221231.pkl')

date_list = tradeDate.get_date_range(20160101, 20211231)

for _dat in tqdm(date_list):
    concept_df = pd.read_pickle(root_path + f'{_dat}.pkl')
    try:
        cur_samples = basic_sample.loc[pd.to_datetime(str(_dat))].index.tolist()
    except:
        print('Error', _dat)
        continue
    res_df = pd.DataFrame(index=cur_samples, columns=cur_samples)
    for samp1 in cur_samples:
        for samp2 in cur_samples:
            if samp1 == '000043.SZ' or samp2 == '000043.SZ':
                cross_num = 0
            else:
                cross_num = (concept_df.loc[samp1] * concept_df.loc[samp2]).sum()
            res_df.loc[samp1, samp2] = cross_num
            # print(_dat, samp1, samp2, cross_num)

    res_df.to_pickle(f'/data/group/800463/fengc/for_xbc/d20240322_saturn_concept_cross_num/{_dat}.pkl')

counter = pd.Series(index=date_list)
for _dat in date_list:
    try:
        res = pd.read_pickle(f'/data/group/800463/fengc/for_xbc/d20240322_saturn_concept_cross_num/{_dat}.pkl')
        counter.loc[_dat] = res.sum().sum()
    except:
        counter.loc[_dat] = 0

print(1)