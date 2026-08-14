# coding: utf-8
# Author：fengchi863
# Date ：2024/5/20 0:22

import pandas as pd
from Zeus.Mimas.v2_0_2.config.path_conf import *

# base_pred = '/data/user/015614/Zeus/pred/Mimas/v4_0_49/rffs_scaler1_pct_AllXgbRegModel/20211201~20220531.csv'
# rank_pred = '/data/user/015614/Zeus/pred/Mimas/v2_0_2/rffs_scaler1_pct_AllXgbRegModel/20211201~20220531.csv'
#
# check1 = pd.read_csv(base_pred, index_col=0)
# check2 = pd.read_csv(rank_pred, index_col=0)
# check1 = check1.rename({'prediction': 'pred_base'})
# check = pd.concat([check1, check2[['prediction']]], axis=1).rename({'prediction': 'pred_rank'})
#
# profit_df = pd.read_hdf(profit_data_fpath)
# profit_df['datelist'] = profit_df.index.get_level_values(0).map(lambda x: x.strftime("%Y%m%d"))
# profit_df['stk_code'] = profit_df.index.get_level_values(1).tolist()
# profit_df['Indexs'] = profit_df[['datelist', 'stk_code']].apply(lambda x: x['stk_code'] + ' ' + x['datelist'], axis=1)
# profit_df = profit_df.set_index('Indexs')
# profit_df['profit'] = profit_df['buy_amt'] * profit_df['pct']
# check = check.join(profit_df['profit'])
# check = check.sort_values('profit', ascending=False)
# check.to_excel('/data/user/015614/junkData/cmp_base_rank.xlsx')


#%% cmp base and rank
base_pred = '/data/user/015614/Zeus/pred/Mimas/v4_0_49/rffs_scaler1_pct_AllXgbRegModel/20211201~20220531.csv'
rank_pred = '/data/user/015614/Zeus/pred/Mimas/v4_0_19/rffs_pct_AllXgbRegModel/20211201~20220531.csv'

check1 = pd.read_csv(base_pred, index_col=0)
check2 = pd.read_csv(rank_pred, index_col=0)
check1 = check1.rename({'prediction': 'pred_base'}, axis=1)
check = pd.concat([check1, check2[['prediction']]], axis=1).rename({'prediction': 'pred_old'}, axis=1)

profit_df = pd.read_hdf(profit_data_fpath)
profit_df['datelist'] = profit_df.index.get_level_values(0).map(lambda x: x.strftime("%Y%m%d"))
profit_df['stk_code'] = profit_df.index.get_level_values(1).tolist()
profit_df['Indexs'] = profit_df[['datelist', 'stk_code']].apply(lambda x: x['stk_code'] + ' ' + x['datelist'], axis=1)
profit_df = profit_df.set_index('Indexs')
profit_df['profit'] = profit_df['buy_amt'] * profit_df['pct']
check = check.join(profit_df['profit'])
check = check.sort_values('profit', ascending=False)
check.to_excel('/data/user/015614/junkData/cmp_base_rank2.xlsx')