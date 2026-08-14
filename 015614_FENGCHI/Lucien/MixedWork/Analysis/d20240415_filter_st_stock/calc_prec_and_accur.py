# coding: utf-8
# Author：fengchi863
# Date ：2024/4/16 15:41

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

#%% 计算召回率
true_set, false_set = set(), set()
for idx in range(len(wind_st)):
    row = wind_st.iloc[idx]
    stk_id = row.name
    entry_dt = row.ENTRY_DT
    pre_entry_dt = tradeDate.get_pre_trade_date(int(entry_dt), 3)
    tmp = pd.read_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{int(pre_entry_dt)}.xlsx')
    if stk_id in tmp['证券代码'].tolist():
        true_set.add(stk_id)
        if stk_id == 620:
            print(1)
    else:
        false_set.add(stk_id)
prec = len(true_set) / (len(true_set) + len(false_set))
# 判断提前1天，71只被ST的个股，21只被提前预测，召回率为29.6%
# 判断提前2天，71只被ST的个股，25只被提前预测，召回率为35.1%
# 判断提前3天，71只被ST的个股，25只被提前预测，召回率为35.1%
# 判断提前4天，71只被ST的个股，25只被提前预测，召回率为35.1%

#%% 计算精确率
date_list = tradeDate.get_date_range(20230101, 20240412)
st_dict = dict()
pred_set = set()
true_set = set()
for dat in tqdm(date_list):
    tmp = pd.read_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{dat}.xlsx')
    if len(tmp) > 0:
        for idx in range(len(tmp)):
            stk_code = tmp.iloc[idx]['证券代码']
            if stk_code == 620:
                print(1)
            # if stk_code in wind_st.index and dat == wind_st.loc[stk_code]['ENTRY_DT']:
            if stk_code in wind_st.index and dat == tradeDate.get_pre_trade_date(wind_st.loc[stk_code]['ENTRY_DT'], 3):
            # if stk_code in wind_st.index:
                true_set.add(stk_code)
                pred_set.add(stk_code)
            else:
                pred_set.add(stk_code)
acc = len(true_set) / len(pred_set)
# 如果只看是否2023年被ST过，那么有42%的准确率
# 如果纳入时间判断，看被纳入前一天是否存在，是21/73 = 28.8%
# 如果纳入时间判断，看被纳入前二天是否存在，是25/73 = 34%
# 如果纳入时间判断，看被纳入前三天是否存在，是25/73 = 34%


