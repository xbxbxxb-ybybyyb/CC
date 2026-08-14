# @Time : 2021/10/20 13:38
# @Author : Zhichen Lu
# @File : threshold_analysis.py
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from online_conf import  model_config_path
import os
from dataApi.tradeDate import get_date_range,get_pre_trade_date

model_conf_list = sorted(list(filter(lambda x : x.endswith('.pkl'),os.listdir(model_config_path))))

threshold_list = {}
for each in model_conf_list:
    _,threshold = pd.read_pickle(f'{model_config_path}{each}')
    threshold_list[int(each[-12:-4])] = threshold


threshold_list = pd.Series(threshold_list)
date_list = get_date_range(threshold_list.index[0],get_pre_trade_date(threshold_list.index[-1],-1))
threshold_list = threshold_list.reindex(date_list).shift(1).fillna(method='pad')
threshold_list.loc[20210406:].dropna().to_excel('./上线以来阈值.xlsx')
from dataApi.sendInfo import send_file
send_file(['015664'],'./上线以来阈值.xlsx')


