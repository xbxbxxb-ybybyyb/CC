# coding: utf-8
# Author：fengchi863
# Date ：2024/4/16 9:26

import pandas as pd
import numpy as np
from dataApi import tradeDate, stockList
from tqdm import tqdm
import datetime

wind_st = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/AShareST/AShareST.h5')
#AShareST = AShareST[(AShareST['S_TYPE_ST'] == 'S') | (AShareST['S_TYPE_ST'] == 'X') | (AShareST['S_TYPE_ST'] == 'L')]
wind_st = wind_st[wind_st['S_TYPE_ST'].isin(['S','X','Y','L'])]

# wind_st = wind_st.query('ENTRY_DT >= 20220101')
wind_st = wind_st['ENTRY_DT']

date_list = tradeDate.get_date_range(20221110, 20240412)
st_dict = dict()
for dat in tqdm(date_list):
    tmp = pd.read_excel(f'/data/user/015614/daily/灰名单生成/黑名单/black_list_{dat}.xlsx')
    if len(tmp) > 0:
        for idx in range(len(tmp)):
            stk_code = tmp.iloc[idx]['股票代码']
            if stk_code not in st_dict.keys():
                st_dict[stk_code] = dat
            else:
                continue


check = pd.DataFrame(pd.Series(st_dict), columns=['最早入池时间'])
wind_st.index = wind_st.index.get_level_values(1).map(lambda x: stockList.trans_windcode2int(x))
wind_st = pd.DataFrame(wind_st)
wind_st.index.name = None
wind_st = wind_st.reset_index().sort_values(['index', 'ENTRY_DT']).drop_duplicates('index', keep='last').set_index('index')
wind_st.index.name = None
wind_st = wind_st.query('ENTRY_DT >= 20230101')

check = wind_st.join(check)
check['是否提前入池'] = check['最早入池时间'] < check['ENTRY_DT']
ratio = (~check['最早入池时间'].isna()).sum() / (~check['ENTRY_DT'].isna()).sum()

