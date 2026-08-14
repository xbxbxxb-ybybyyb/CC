# coding: utf-8
# Author：fengchi863
# Date ：2024/4/15 14:51

import pandas as pd
from dataApi.stockList import trans_windcode2int

st_stk_list = pd.read_excel('/data/user/015614/junkData/ST新规明细和宽基指数(含创业板).xlsx', sheet_name='ST新规名单')

deal_pool = pd.read_excel('/data/group/800463/xiely/save-file/forFc/risk/股票池-20240415.xls')
event_pool = pd.read_excel('/data/group/800463/xiely/save-file/forFc/risk/事件池-20240415.xls')

st_stk_list = st_stk_list['Unnamed: 0'].apply(lambda x: trans_windcode2int(x)).tolist()
st_stk_list = list(map(lambda x: str(x).zfill(6), st_stk_list))
deal_stk_list = deal_pool['证券代码'].tolist()
event_stk_list = event_pool['证券代码'].apply(lambda x: str(x).zfill(6)).tolist()

deal_st_cross = list(set(deal_stk_list).intersection(set(st_stk_list)))
event_st_cross = list(set(event_stk_list).intersection(set(st_stk_list)))

print(f'交易池需要剔除{len(deal_st_cross)}/{len(deal_stk_list)}只个股')
print(f'事件池需要剔除{len(event_st_cross)}/{len(event_stk_list)}只个股')
