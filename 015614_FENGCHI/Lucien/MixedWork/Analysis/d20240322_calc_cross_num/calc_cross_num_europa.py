# coding: utf-8
# Author：fengchi863
# Date ：2024/3/22 10:50

import pandas as pd
import numpy as np
from LucienUtil import IO
from dataApi import tradeDate
from tqdm import tqdm
import time
import os

# root_path = '/data/user/015614/daily/basic/basic_wind_sw_history20241014/BlockData/daily_Wind&SW/'
root_path = '/data/user/015614/daily/basic/basic_wind_sw_history_everydayfix/BlockData/daily_Wind&SW/'
# root_path = '/data/user/015614/daily/basic/basic_wind_sw_history4/BlockData/daily_Wind&SW/'
# basic_sample = pd.read_pickle('/data/user/018107//share_file/for_fc/europa_index_20160101_20241011.pkl')
basic_sample = pd.read_pickle('/data/user/018107/share_file/for_fc/20250114_europa_index_20160101_20250112.pkl')
# basic_sample = pd.read_pickle('/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20220831.pkl')

# date_list = tradeDate.get_date_range(20160101, 20211231)
# date_list = tradeDate.get_date_range(20220101, 20220531)
# date_list = tradeDate.get_date_range(20160101, 20240221)
# date_list = tradeDate.get_date_range(20160104, 20240513)
# date_list = tradeDate.get_date_range(20240514, 20241011)
# date_list = tradeDate.get_date_range(20241018, 20241023)
# date_list = tradeDate.get_date_range(20241023, 20250109)
date_list = tradeDate.get_date_range(20160105, 20250109)

for _dat in tqdm(date_list):
    pre_dat_ = tradeDate.get_pre_trade_date(_dat) if _dat >= 20160105 else 20160104
    while True:
        if os.path.exists(root_path + f'{pre_dat_}.pkl'):
            concept_df = pd.read_pickle(root_path + f'{pre_dat_}.pkl')
            break
        else:
            print('等待' + root_path + f'{pre_dat_}.pkl')
            time.sleep(60)
    try:
        cur_samples = basic_sample.loc[pd.to_datetime(str(_dat))].index.tolist()
    except:
        print('Error', _dat)
        continue
    # res_df = pd.DataFrame(index=cur_samples, columns=cur_samples)
    # for samp1 in cur_samples:
    #     for samp2 in cur_samples:
    #         if samp1 == '000043.SZ' or samp2 == '000043.SZ':
    #             cross_num = 0
    #         else:
    #             cross_num = (concept_df.loc[samp1] * concept_df.loc[samp2]).sum()
    #         res_df.loc[samp1, samp2] = cross_num
    #         # print(_dat, samp1, samp2, cross_num)

    concept_df = concept_df.loc[cur_samples]

    concept_df2 = concept_df.copy()
    concept_np = concept_df.values
    concept_np2 = concept_df2.values
    check = concept_np2.dot(concept_np.T)
    res_df = pd.DataFrame(check, index=concept_df2.index.tolist(), columns=concept_df.index.tolist())

    # res_df.to_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
    # res_df.to_pickle(f'/data/user/015614/shared/for_zwh/d20240410_europa_concept_cross_num/{_dat}.pkl')
    res_df.to_pickle(f'/data/group/800463/data/concept_data/europa/20250114/{_dat}.pkl')
    print(_dat, res_df.sum().sum())
    # from dataApi.sendInfo import send_message
    # send_message(f'{_dat}已生成')

# counter = pd.Series(index=date_list)
# for _dat in date_list:
#     try:
#         res = pd.read_pickle(f'/data/group/800463/fengc/for_xbc/d20240410_europa_concept_cross_num/{_dat}.pkl')
#         counter.loc[_dat] = res.sum().sum()
#     except:
#         counter.loc[_dat] = 0

from scipy.io import mmread, mmwrite, mminfo
# from scipy.sparse import coo_matrix
#
# coo = coo_matrix((res_df.values.reshape(-1), (list(np.arange(res_df.shape[1])) * res_df.shape[0], list(np.arange(res_df.shape[0])) * res_df.shape[1])), shape=res_df.shape)
