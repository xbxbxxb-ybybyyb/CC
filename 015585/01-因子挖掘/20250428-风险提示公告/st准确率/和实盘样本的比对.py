import pandas as pd
import os
from xquant.factordata import FactorData
import IO
import numpy as np
s = FactorData()


df_st = s.get_factor_value('WIND_AShareST')
risk_list_20241231 = list(df_st[((df_st['REMOVE_DT'].isnull()) | (df_st['REMOVE_DT'] >= '20250416')) \
                       & (df_st['ENTRY_DT'] <= '20250415') & (df_st['S_TYPE_ST'] != 'R')]['S_INFO_WINDCODE']) # 20250415 时候仍然有问题的股票
df_st_2025 = df_st[(df_st['ENTRY_DT'] >= '20250416') & (df_st['ENTRY_DT'] <= '20250430')]
df_st_2025_filter = df_st_2025[df_st_2025['S_TYPE_ST'] != 'R'] # 非“恢复上市”均考虑


list_xly = ['000736.SZ', '002306.SZ', '000430.SZ', '000697.SZ', '603021.SH',
       '003032.SZ', '300044.SZ', '002211.SZ', '002076.SZ', '300093.SZ',
       '300344.SZ', '600265.SH', '605199.SH', '603580.SH', '300152.SZ',
       '002620.SZ', '002630.SZ', '002868.SZ', '002058.SZ', '600525.SH',
       '300716.SZ', '002231.SZ', '300198.SZ', '300477.SZ']

for i in list_xly:
    if i in risk_list_20241231:
        print(i)

for i in list_xly:
    if i in list(df_st_2025_filter['S_INFO_WINDCODE']):
        print(i)
    else:
        print(i, 'not in ')
