import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import IO

s = FactorData()
df = s.get_factor_value('WIND_AShareIncome',ANN_DT = ['>=20230101'])
df_filter = df[df['STATEMENT_TYPE'] == '408001000']

for col in ['ANN_DT','OPDATE']:
    df_filter[col] = df_filter[col].apply(pd.Timestamp)
# df_filter['timedelta'] = df_filter['OPDATE'] - df_filter['ANN_DT']
# 单独看ANN_DT
df_filter['OPHOUR'] = df_filter['OPDATE'].apply(lambda x : x.strftime('%H:%M:%S'))
df_filter[df_filter['OPHOUR'] <= '06:00'].shape
tmp = df_filter['OPHOUR']

