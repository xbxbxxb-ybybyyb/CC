# coding: utf-8
# Author：fengchi863
# Date ：2025/4/16 9:47

import pandas as pd
from dataApi.tradeDate import get_date_range

date_list = get_date_range(20250101, 20250413)
for date in date_list:
    print(date)
    try:
        tmp = pd.read_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{date}.xlsx', sheet_name='Sheet1')
    except:
        tmp = pd.read_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{date}.xlsx', sheet_name='黑名单')
    tmp['证券代码'] = tmp['证券代码'].map(lambda x: str(x).zfill(6))
    tmp.to_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{date}.xlsx', index=False)