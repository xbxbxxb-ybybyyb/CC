# coding: utf-8
# Author：fengchi863
# Date ：2024/4/15 16:45

import pandas as pd
import numpy as np
from dataApi import tradeDate, stockList
from tqdm import tqdm
import datetime
import os

wind_st = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/AShareST/AShareST.h5')
wind_st = wind_st[wind_st['S_TYPE_ST'].isin(['S'])]

# wind_st = wind_st.query('ENTRY_DT >= 20220101')
wind_st = wind_st[['ENTRY_DT', 'REMOVE_DT', 'S_TYPE_ST']]

wind_st.index = wind_st.index.get_level_values(1).map(lambda x: stockList.trans_windcode2int(x))
wind_st.index.name = None
wind_st = wind_st.loc[(wind_st.index.map(lambda x: str(x).startswith('688'))) == False]   # 剔除科创板
wind_st = wind_st.query('ENTRY_DT >= 20230101')
wind_st = wind_st.reset_index().sort_values(['index', 'ENTRY_DT']).drop_duplicates('index', keep='first').set_index('index')
wind_st.index.name = None

date_list = tradeDate.get_date_range(20210519, 20240412)
st_dict = dict()
for dat in tqdm(date_list):
    tmp = pd.read_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{dat}.xlsx')
    if len(tmp) > 0:
        for idx in range(len(tmp)):
            stk_code = tmp.iloc[idx]['证券代码']
            if stk_code not in st_dict.keys():
                st_dict[stk_code] = dat
            else:
                continue

    # if os.path.exists(f'/data/group/800463/stock_list/defer_reply_list/defer_reply_list_{dat}.xlsx'):
    #     tmp = pd.read_excel(f'/data/group/800463/stock_list/defer_reply_list/defer_reply_list_{dat}.xlsx')
    #     if len(tmp) > 0:
    #         for idx in range(len(tmp)):
    #             stk_code = tmp.iloc[idx]['证券代码']
    #             if stk_code not in st_dict.keys():
    #                 st_dict[stk_code] = dat
    #             else:
    #                 continue


check = pd.DataFrame(pd.Series(st_dict), columns=['最早入池时间'])

check = wind_st.join(check)
check['是否提前入池'] = check['最早入池时间'] < check['ENTRY_DT']
check = check.sort_values('ENTRY_DT')
ratio = (~check['最早入池时间'].isna()).sum() / (~check['ENTRY_DT'].isna()).sum()

wind_st_raw = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/AShareST/AShareST.h5')
wind_st_raw['Ticker'] = wind_st_raw.index.get_level_values(1)
a = wind_st_raw.query('Ticker == "300029.SZ"')
a = wind_st_raw.query('ENTRY_DT >= 20240412')
wind_st_raw['ENTRY_DT']