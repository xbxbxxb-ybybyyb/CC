# @Time : 2021/9/30 8:32
# @Author : Zhichen Lu
# @File : use_pre_day_code_list.py
import pandas as pd
from online_conf import code_list_path
from dataApi.tradeDate import get_pre_trade_date
import os

date = 20210929
pre_code_list = pd.read_pickle(f'{code_list_path}{get_pre_trade_date(date)}.pkl')
pd.to_pickle(pre_code_list,f'{code_list_path}{date}.pkl')

signal_930 = pd.read_pickle(f'/data/group/800319/strategy_local_path3/morning_model/val_sign/{date}.pkl')
pd.to_pickle(signal_930,f'/data/group/800319/strategy_local_path3/morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl')