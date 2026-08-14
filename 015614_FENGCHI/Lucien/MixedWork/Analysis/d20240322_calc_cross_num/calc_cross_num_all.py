# coding: utf-8
# Author：fengchi863
# Date ：2024/3/22 10:50

import pandas as pd
import numpy as np
from LucienUtil import IO
from dataApi import tradeDate
from tqdm import tqdm
import os

# root_path = '/data/user/015614/daily/basic/basic_wind_sw_history4/BlockData/daily_Wind&SW/'
root_path = '/data/user/015614/daily/basic/basic_wind_sw_history20240619/BlockData/daily_Wind&SW/'
# basic_sample = pd.read_pickle('/data/user/018107//share_file/for_fc/europa_index_20160101_20240531.pkl')

# date_list = tradeDate.get_date_range(20160101, 20211231)
# date_list = tradeDate.get_date_range(20220101, 20220531)
# date_list = tradeDate.get_date_range(20160101, 20240221)
# date_list = tradeDate.get_date_range(20240221, 20240513)
# date_list = tradeDate.get_date_range(20240513, 20240603)
date_list = tradeDate.get_date_range(20240601, 20240618)

for _dat in tqdm(date_list):
    pre_dat_ = tradeDate.get_pre_trade_date(_dat)
    concept_df = pd.read_pickle(root_path + f'{pre_dat_}.pkl')
    cur_samples = concept_df.index.tolist()

    concept_df2 = concept_df.copy()
    concept_np = concept_df.values
    concept_np2 = concept_df2.values
    check = concept_np2.dot(concept_np.T)
    res_df = pd.DataFrame(check, index=concept_df2.index.tolist(), columns=concept_df.index.tolist())

    os.makedirs('/data/user/015614/shared/for_all/d20240618_allA_concept_cross_num/', exist_ok=True)
    # os.makedirs('/data/user/015614/shared/for_xly/d20240618_allA_concept_cross_num/', exist_ok=True)
    # os.makedirs('/data/user/015614/shared/for_cjq/d20240618_allA_concept_cross_num/', exist_ok=True)

    res_df.to_pickle(f'/data/user/015614/shared/for_all/d20240618_allA_concept_cross_num/{_dat}.pkl')
    # res_df.to_pickle(f'/data/user/015614/shared/for_xly/d20240618_allA_concept_cross_num/{_dat}.pkl')
    # res_df.to_pickle(f'/data/user/015614/shared/for_cjq/d20240618_allA_concept_cross_num/{_dat}.pkl')
    print(_dat, res_df.sum().sum())

# counter = pd.Series(index=date_list)
# for _dat in date_list:
#     try:
#         res = pd.read_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
#         counter.loc[_dat] = res.sum().sum()
#     except:
#         counter.loc[_dat] = 0