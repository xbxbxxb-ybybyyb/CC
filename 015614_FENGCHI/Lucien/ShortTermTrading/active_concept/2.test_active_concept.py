# coding: utf-8
# Author：fengchi863
# Date ：2023/10/25 16:05

"""
方案一：直接参与各个活跃板块前2只涨停的 VS 参与各个行业前两只涨停的
方案二：叠加策略，这个好像无法实现
"""
import pandas as pd
import numpy as np
from Zeus.Europa.v4_0_3.path_conf import *
from xquant.factordata import FactorData
from itertools import product
from tqdm import tqdm
from dataApi.tradeDate import get_date_range
fd = FactorData()

rollDays = 4
active_concept = pd.read_pickle('/data/user/015614/TEST/active_concept_test/active_concept_fulldays.pkl')
active_concept = active_concept.sort_index()
active_concept = active_concept.shift(1).fillna(method='bfill') # 推移一天，不用未来信息
active_concept = (active_concept.rolling(rollDays).sum() >= 1).fillna(0).loc[get_date_range(20160101, 20221231)]

# pred_data_path ='/data/user/015614/Zeus/pred/Europa/v4_0_3/fsv10_pct_AllXgbRegModel/'
# period_list = ['period1', 'period2', 'period3']
# testfit_list = ['test', 'fit']

# for period in period_list:
#     for testfit in testfit_list:
#         start_date = date_config[period][f'{testfit}_start_date']
#         end_date = date_config[period][f'{testfit}_end_date']
#         pred_data_fpath = pred_data_path + f'{start_date}~{end_date}.csv'
#         pred_data = pd.read_csv(pred_data_fpath)
#
#         date_list = list(map(lambda x: int(x), fd.tradingday(start_date, end_date)))
#         for dat in date_list:
#             today_active_concept_list = active_concept.loc[dat][active_concept.loc[dat]].index.tolist()
#             for today_active_concept in today_active_concept_list:
#                 today_wind_stk_df = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/{dat}.pkl')
#                 cmpn_stock = today_wind_stk_df[today_active_concept][today_wind_stk_df[today_active_concept]==1].index.tolist()

europa_label_data_path = f'/data/group/800463/sunss/profit/europa/20230925/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5'
data_all_fpath = f'/data/user/018107/share_file/for_fc/europa/20230329_new/factor_df_all_20160101_20230331.pkl'

start_date = 20160101
# start_date = 20221028
end_date = 20221231
# end_date = 20231027
# end_date = 20160130
date_list = list(map(lambda x: int(x), fd.tradingday(start_date, end_date)))
basic_data = pd.read_pickle(data_all_fpath)

dat_stk_tuple_list = list()
for dat in tqdm(date_list):
    today_active_concept_list = active_concept.loc[dat][active_concept.loc[dat]].index.tolist()
    # today_active_stock_list = list()
    for today_active_concept in today_active_concept_list:
        # NOTE: 从20221028开始，可能是由于按天更新的缘故，每天的这个表的列的数量减少为200多，其实应该都在600左右 比如884133.WI就没有
        # NOTE: 重跑一遍之后，这个问题没有了
        today_wind_stk_df = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/daily_Wind&SW/{dat}.pkl')
        try:
            tmp_cmpn_stock = today_wind_stk_df[today_active_concept][today_wind_stk_df[today_active_concept] == 1].index.tolist()
        except:
            print(dat, today_active_concept)
            continue
        # today_active_stock_list = list(set(today_active_stock_list + tmp_cmpn_stock))
        dat_stk_tuple_list += list(product([pd.to_datetime(str(dat))], tmp_cmpn_stock, [today_active_concept]))

dat_stk_df = pd.DataFrame(dat_stk_tuple_list, columns=['dt', 'Ticker', 'concept'])
dat_stk_df = dat_stk_df.groupby(['dt', 'Ticker'])['concept'].apply(lambda x: ','.join(x))
basic_data['concept'] = np.nan
dat_stk_df = dat_stk_df.loc[list(set(dat_stk_df.index).intersection(set(basic_data.index)))]

dat_stk_df = dat_stk_df.sort_index()
basic_data = basic_data.sort_index()
basic_data.loc[dat_stk_df.index, 'concept'] = dat_stk_df.values
basic_data.to_pickle(f'/data/user/015614/TEST/active_concept_test/basic_data_concept_roll{rollDays}.pkl')   # 如果concept有值，则为活跃概念


# check1 = pd.read_pickle(f'/data/user/015614/TEST/active_concept_test/basic_data_concept.pkl')
# check2 = pd.read_pickle(f'/data/user/015614/TEST/active_concept_test/basic_data_concept_roll{rollDays}.pkl')
# check1 = check1['concept']
# check2 = check2['concept']
# check1['concept2'] = check2.values
# aaa = check1[['concept', 'concept2']]