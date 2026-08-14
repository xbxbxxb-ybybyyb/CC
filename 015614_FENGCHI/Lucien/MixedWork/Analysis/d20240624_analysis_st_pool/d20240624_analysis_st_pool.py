# coding: utf-8
# Author：fengchi863
# Date ：2024/6/24 10:57

import pandas as pd
import numpy as np
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

# st_pool = pd.read_excel('/data/user/015614/junkData/证投部投资池潜在ST股票预警.xlsx')
st_pool = pd.read_excel('/data/user/015614/junkData/证投部投资池潜在ST股票预警20240704.xlsx')
st_pool['st_date'] = st_pool['预警日期'].apply(lambda x: pd.to_datetime(x).strftime('%Y%m%d'))
st_pool['stk_id'] = st_pool['股票代码']

st_pool['white'] = 0
st_pool['grey'] = 0
st_pool['black'] = 0
st_pool['manual'] = 0
st_pool['pre_dt'] = 0
st_pool['pre_st'] = 0
st_pool['after_dt'] = 0
st_pool['share_comp_restrict'] = 0
st_pool['defer_reply'] = 0

for idx in range(len(st_pool)):
    print(idx)
    tmp = st_pool.iloc[idx]
    # trade_date = tmp['st_date']
    trade_date = '20240704'
    stk_id = int(tmp['stk_id'])

    tradeDatestr = str(trade_date)
    tradeDatestr = s.tradingday(tradeDatestr, -1)[0]
    yesDatestr = s.tradingday(tradeDatestr, -2)[0]

    white_fpath = f'/data/group/800463/stock_list/white_list/{tradeDatestr}.xls'
    grey_fpath = f'/data/group/800463/stock_list/grey_list/grey_list_{tradeDatestr}.xlsx'
    black_fpath = f'/data/group/800463/stock_list/black_list/black_list_{tradeDatestr}.xlsx'
    manual_fpath = f'/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx'
    pre_dt_fpath = f'/data/group/800463/stock_list/pre_dt_list/pre_dt_list_{tradeDatestr}.xlsx'
    pre_st_fpath = f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{yesDatestr}.xlsx'
    after_dt_fpath = f'/data/group/800463/stock_list/after_dt_list/after_dt_list_{yesDatestr}.xlsx'
    share_comp_restrict_fpath = f'/data/group/800463/stock_list/share_comp_restrict_list/share_comp_restrict_list_{tradeDatestr}.xlsx'
    defer_reply_fpath = f'/data/group/800463/stock_list/defer_reply_list/defer_reply_list_{yesDatestr}.xlsx'

    white_list = pd.read_excel(white_fpath)['证券代码'].tolist()
    grey_list = pd.read_excel(grey_fpath)['股票代码'].tolist()
    black_list = pd.read_excel(black_fpath)['股票代码'].tolist()
    manual_list = pd.read_excel(manual_fpath)['证券代码'].tolist()
    pre_dt_list = pd.read_excel(pre_dt_fpath)['证券代码'].tolist()
    pre_st_list = pd.read_excel(pre_st_fpath)['证券代码'].tolist()
    after_dt_list = pd.read_excel(after_dt_fpath)['证券代码'].tolist()
    share_comp_restrict_list = pd.read_excel(share_comp_restrict_fpath)['证券代码'].tolist()
    defer_reply_list = pd.read_excel(defer_reply_fpath)['证券代码'].tolist()

    if str(stk_id).zfill(6) in white_list: st_pool.loc[idx, 'white'] = 1
    if stk_id in grey_list: st_pool.loc[idx, 'grey'] = 1
    if stk_id in black_list: st_pool.loc[idx, 'black'] = 1
    if stk_id in manual_list: st_pool.loc[idx, 'manual'] = 1
    if stk_id in list(map(lambda x: int(x[:-3]), pre_dt_list)): st_pool.loc[idx, 'pre_dt'] = 1
    if stk_id in pre_st_list: st_pool.loc[idx, 'pre_st'] = 1
    if stk_id in after_dt_list: st_pool.loc[idx, 'after_dt'] = 1
    if stk_id in share_comp_restrict_list: st_pool.loc[idx, 'share_comp_restrict'] = 1
    if stk_id in defer_reply_list: st_pool.loc[idx, 'defer_reply'] = 1

print(1)
st_pool = st_pool.drop('预警详情', axis=1)
st_pool.to_excel('/data/user/015614/junkData/st_pool_1.xlsx')