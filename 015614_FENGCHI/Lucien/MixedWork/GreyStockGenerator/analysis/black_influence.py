# coding: utf-8
# Author：fengchi863
# Date ：2025/6/11 10:04

import pandas as pd
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_int2windcode
from itertools import product



date_list = get_date_range(20240101, 20250610)
europa_df = pd.read_pickle('/data/user/018107/share_file/for_fc/20250611_europa_filter_basic_20240101_20250610.pkl')
black_df = pd.DataFrame()
index_list = list()
print(1)
for _dat in date_list:
    black_list = pd.read_excel(f'/data/group/800463/stock_list/share_comp_restrict_list/share_comp_restrict_list_{_dat}.xlsx', index_col=0).index.tolist()
    black_list = list(map(lambda x: trans_int2windcode(x), black_list))
    index_list.extend(list(product([pd.to_datetime(str(_dat))], black_list)))

black_df = pd.DataFrame(index=index_list)
europa_df.shape
black_df.shape
common_index = list(set(europa_df.index).intersection(set(black_df.index)))
common_df = europa_df.loc[common_index]

profit_df = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fixnew/001/LabelProfit_zt_twap_0.10_2000_300_SH100_SZ10.h5')
concat_df = pd.merge(common_df, profit_df, on=['dt', 'Ticker'], how='left')

#%% 统计结果
concat_df['pct'].describe()
concat_df['profit'] = concat_df['pct'] * concat_df['buy_amt']
concat_df['profit'].describe()
concat_df['profit'].sum()
concat_df = concat_df.sort_index()

# concat_df.to_excel('/data/user/015614/junkData/black_influence.xlsx')

#%% 统计带有信号的样本
signal_list = list()
for _dat in date_list:
    diff_df = pd.read_excel(f'/data/group/800463/日内强势股/cpp_log_parse/模型差异/{_dat}/模型差异New_{_dat}_prod.xlsx', sheet_name='本地投票结果').reset_index()
    diff_df = diff_df.query(f'本地投票结果 == True')
    black_list = list(map(lambda x: trans_int2windcode(x), diff_df['Ticker'].tolist()))
    signal_list.extend(list(product([pd.to_datetime(str(_dat))], black_list)))

signal_df = pd.DataFrame(index=signal_list)
common_signal_index = list(set(common_df.index).intersection(set(signal_df.index)))


print(1)

common_df = europa_df.loc[common_signal_index]

profit_df = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fixnew/001/LabelProfit_zt_twap_0.10_2000_300_SH100_SZ10.h5')
concat_df = pd.merge(common_df, profit_df, on=['dt', 'Ticker'], how='left')

#%% 统计结果
concat_df['pct'].describe()
concat_df['profit'] = concat_df['pct'] * concat_df['buy_amt']
concat_df['profit'].describe()
concat_df['profit'].sum()
concat_df = concat_df.sort_index()
concat_df.to_excel('/data/user/015614/junkData/black_influence2.xlsx')