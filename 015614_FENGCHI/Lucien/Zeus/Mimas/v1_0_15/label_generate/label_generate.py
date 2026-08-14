# coding: utf-8
# Author：fengchi863
# Date ：2024/8/28 13:16

import sys
import os
import importlib
import pandas as pd
import numpy as np
from Zeus.Mimas.v1_0_15.config.path_conf import *
from Zeus.Mimas.v1_0_15.config.strat_conf import *

if len(sys.argv) > 1:
    config_flag = sys.argv[1]
else:
    config_flag = 'config1'

module_name = f'Zeus.Mimas.v1_0_15.config.path_conf'
module = importlib.import_module(module_name)
PT = getattr(module, config_flag)
data_fpath = PT['data_fpath']
profit_data_fpath = PT['profit_data_fpath']
label = PT['label']

label_df = pd.read_pickle(data_fpath)
profit_df = pd.read_hdf(profit_data_fpath)

profit_df = profit_df.loc[label_df.index]
label_list = list(filter(lambda x: x.startswith('label'), label_df.columns.tolist()))
print(label_list)
print(profit_df.columns.tolist())
label1_data = label_df[label_list]
label2_data = profit_df[['pct', 'pct_T', 'pct_T1']]
label_data = pd.concat([label1_data, label2_data], axis=1)

def func4label1(x): # 和pct的相关性在0.99以上
    """根据当日封板状态对收益标签进行划分，如果当日炸过板，就对标签-0.01，如果当日尾盘炸板没封住，就对标签-0.02"""
    if x['label_pattern'] == 3:
        res = x['pct'] - 0.01
    elif x['label_pattern'] == 2:
        res = x['pct'] - 0.02
    elif x['label_pattern'] == 4:
        res = x['pct']
    elif x['label_pattern'] == 0:
        res = x['pct'] - 0.03
    else:
        res = x['pct']
    return res

def func4label2(x):
    """更多考虑当日收益，淡化次日收益的影响"""
    res = (x['pct_T'] * 8 + x['pct_T1'] * 2) / 10
    return res

def func4label3(x):
    """更多考虑次日之后的收益，忽略当天的收益"""
    res = (x['pct_T'] * 3 + x['pct_T1'] * 7) / 10
    return res

# #%% label1的计算
# label_data = label_data
# label_data['self_pct_label1'] = label_data[['label_pattern', 'pct']].apply(lambda x: func4label1(x), axis=1)
# os.makedirs(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/', exist_ok=True)
# label_data.to_pickle(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/self_pct_label1.pkl')   # 命名方式为pct 2 label1
# print(f'generate self_label1 to /data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/self_pct_label1.pkl')

#%% label2的计算
label_data = label_data.copy()
label_data['self_pct_label2'] = label_data[['pct_T', 'pct_T1']].apply(lambda x: func4label2(x), axis=1)
os.makedirs(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/', exist_ok=True)
label_data.to_pickle(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/self_pct_label2.pkl')
print(f'generate self_label2 to /data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/self_pct_label2.pkl')

#%% label3的计算
label_data = label_data.copy()
label_data['self_pct_label3'] = label_data[['pct_T', 'pct_T1']].apply(lambda x: func4label3(x), axis=1)
os.makedirs(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/', exist_ok=True)
label_data.to_pickle(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/self_pct_label3.pkl')
print(f'generate self_label3 to /data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/self_pct_label3.pkl')

check = label_data.corr()
print('check')