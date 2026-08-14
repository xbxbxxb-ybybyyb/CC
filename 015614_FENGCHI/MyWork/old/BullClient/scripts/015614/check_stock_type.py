# coding: utf-8
# Author：fengchi863
# Date ：2020/8/28 15:45

import pandas as pd
from BullClient.conf.path_conf import stock_type_path

type_1_1 = pd.read_pickle(stock_type_path + 'type_1_1.pkl')
print(type_1_1.sum().sum())
type_1_2 = pd.read_pickle(stock_type_path + 'type_1_2.pkl')
print(type_1_2.sum().sum())

type_1 = pd.read_pickle(stock_type_path + 'type_2.pkl')
print(type_1.sum().sum())
type_1 = pd.read_pickle(stock_type_path + 'type_3.pkl')
print(type_1.sum().sum())
type_1 = pd.read_pickle(stock_type_path + 'type_4.pkl')
print(type_1.sum().sum())
type_1 = pd.read_pickle(stock_type_path + 'type_5.pkl')
print(type_1.sum().sum())
type_1 = pd.read_pickle(stock_type_path + 'type_6.pkl')
print(type_1.sum().sum())
type_1 = pd.read_pickle(stock_type_path + 'type_7.pkl')
print(type_1.sum().sum())
type_1 = pd.read_pickle(stock_type_path + 'type_8.pkl')
print(type_1.sum().sum())
