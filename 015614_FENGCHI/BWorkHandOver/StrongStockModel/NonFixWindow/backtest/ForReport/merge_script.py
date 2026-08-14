# @Time : 2022/5/12 19:57
# @Author : Zhichen Lu
# @File : merge_script.py
import pandas as pd
import numpy as np
import os

source1 = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储20220512Append/'
source2 = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储20220512/'

target = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储20220512Final/'

tag = 'XGB_DTC_Matrix_Light_Cat'

# for window in range(1,9):
#     long1 = pd.read_pickle(f'{source1}/{tag}/long/signal_long_{window}_pct_0.05.pkl')
#     long2 = pd.read_pickle(f'{source2}/{tag}/long/signal_long_{window}_pct_0.05.pkl')
#     print(long1[0].index[0],long1[0].index[-1],long2[0].index[0],long2[0].index[-1])
#     res = []
#     for item1,item2 in list(zip(long1,long2)):
#         temp = pd.concat([item1,item2]).sort_index()
#         res.append(temp)
#     target_long_file = f'{target}/{tag}/long/signal_long_{window}_pct_0.05.pkl'
#     if not os.path.exists(os.path.split(target_long_file)[0]):
#         os.makedirs(os.path.split(target_long_file)[0])
#     pd.to_pickle(res,target_long_file)


for window in range(1,9):
    short1 = pd.read_pickle(f'{source1}/{tag}/short/signal_short_{window}_pct_0.pkl')
    short2 = pd.read_pickle(f'{source2}/{tag}/short/signal_short_{window}_pct_0.pkl')
    print(short1[0].index[0],short1[0].index[-1],short2[0].index[0],short2[0].index[-1])
    res = []
    for item1,item2 in list(zip(short1,short2)):
        temp = pd.concat([item1,item2]).sort_index()
        res.append(temp)
    target_short_file = f'{target}/{tag}/short/signal_short_{window}_pct_0.pkl'
    if not os.path.exists(os.path.split(target_short_file)[0]):
        os.makedirs(os.path.split(target_short_file)[0])
    pd.to_pickle(res,target_short_file)