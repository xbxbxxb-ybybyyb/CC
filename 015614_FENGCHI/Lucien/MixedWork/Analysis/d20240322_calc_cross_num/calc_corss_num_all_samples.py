# coding: utf-8
# Author：fengchi863
# Date ：2024/4/24 15:44

import pandas as pd
from dataApi import tradeDate
from tqdm import tqdm

# root_path = '/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/daily_Wind&SW/'
# root_path = '/data/user/015614/daily/basic/basic_wind_sw_history4/BlockData/daily_Wind&SW/'
root_path = '/data/user/015614/daily/basic/basic_wind_sw_history20240604//BlockData/daily_Wind&SW/'
# basic_sample = pd.read_pickle('/data/group/800463/sunss/europa/20231102/factor_df_all_20160101_20221130.pkl')
basic_sample = pd.read_pickle('/data/user/018107//share_file/for_fc/europa_index_20160101_20240531.pkl')

# date_list = tradeDate.get_date_range(20160101, 20220531)
date_list = tradeDate.get_date_range(20240514, 20240531)

for _dat in tqdm(date_list):
    pre_dat_ = tradeDate.get_pre_trade_date(_dat)
    concept_df = pd.read_pickle(root_path + f'{pre_dat_}.pkl')
    concept_df2 = concept_df.loc[basic_sample.loc[pd.to_datetime(str(_dat))].index.tolist()]
    concept_np = concept_df.values
    concept_np2 = concept_df2.values
    check = concept_np2.dot(concept_np.T)
    res_df = pd.DataFrame(check, index=concept_df2.index.tolist(), columns=concept_df.index.tolist())
    # res_df.to_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
    # res_df.to_pickle(f'/data/user/015614/shared/for_zwh/d20240410_europa_concept_cross_num/{_dat}.pkl')
    res_df.to_pickle(f'/data/user/015614/shared/for_sss/d20240424_allA_concept_cross_num/{_dat}.pkl')

# counter = pd.Series(index=date_list)
# for _dat in date_list:
#     try:
#         res = pd.read_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
#         counter.loc[_dat] = res.sum().sum()
#     except:
#         counter.loc[_dat] = 0