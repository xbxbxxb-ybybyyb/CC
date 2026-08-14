# coding: utf-8
# Author：fengchi863
# Date ：2025/4/15 13:50

import pandas as pd
from dataApi.tradeDate import get_date_range
from tqdm import tqdm

# date_list = get_date_range(20231106, 20250414)
# res = pd.DataFrame()
#
# for date in date_list:
#     local_factor_path = f'/data/group/800463/project/project1_prod/right_v2309/daily_data/{date}_metis/all_factor_zt_merge_v2309_{date}_metis.pkl'
#     factor = pd.read_pickle(local_factor_path)['trigger_time']
#     res = pd.concat([res, factor], axis=0)
#
# deal_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录Metis-20250414.xlsx')
# deal_df['发生日期'] = deal_df['发生日期'].apply(lambda x: pd.to_datetime(x))
# deal_df = deal_df.set_index(['发生日期', '证券代码'])
# res.loc[deal_df.index].to_excel('/data/user/015614/junkData/Metis买入记录修正.xlsx')


date_list = get_date_range(20250206, 20250411)
res = pd.DataFrame()

for date in date_list:
    local_factor_path = f'/data/group/800463/project/project1_prod/right_v2412_BJ/daily_data/{date}/all_factor_zt_merge_v2412_BJ_{date}.pkl'
    factor = pd.read_pickle(local_factor_path)['ul_price']
    res = pd.concat([res, factor], axis=0)

deal_df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录Bj-20250415.xlsx')
deal_df['发生日期'] = deal_df['买入日期'].apply(lambda x: pd.to_datetime(x))
deal_df = deal_df.set_index(['发生日期', '证券代码'])
res.loc[deal_df.index].to_excel('/data/user/015614/junkData/BJ买入记录修正.xlsx')
