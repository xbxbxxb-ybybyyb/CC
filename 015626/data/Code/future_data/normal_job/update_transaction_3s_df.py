import json
from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import pickle
import numpy as np
import glob
from multiprocessing import Pool

def get_df_3s(path):
    df = pd.read_csv(path,index_col=0,parse_dates=True)[['BuyUniqueOrderNum','BuyTradeNum','SellUniqueOrderNum','SellTradeNum']]
    df.index.name = 'dt'
    df = df.loc[df.index.time < datetime.time(14,57)]
    df['Ticker'] = path.split('/')[-1].replace('.csv','')
    df = df.reset_index().set_index(['dt','Ticker'])
    df = df.fillna(0)
    return df

print('start')
pathlist = glob.glob('/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction_to_3s/CSV/ZZ500/*/*.csv')

print(len(pathlist))

dflist = []
with Pool(24) as pool:
    dflist = pool.map(get_df_3s, pathlist)

print('csv done!')
df3s = pd.concat(dflist, axis = 0)
print('concat done!')
df3s = df3s.sort_index()
print('sort done!')
df3s = df3s.unstack()

for col in df3s.columns.get_level_values(0).unique():
    df3s[col].to_pickle('/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction_to_3s/pickle/%s.pkl'%col)