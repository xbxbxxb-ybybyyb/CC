# @Time : 2021/7/9 8:33
# @Author : Zhichen Lu
# @File : Emergency.py
import pandas as pd
import shutil
from online_conf import local_config_path,code_list_path
from dataApi.tradeDate import get_pre_trade_date

date = 20210823
pre_day = get_pre_trade_date(date)
pre_pre_day = get_pre_trade_date(pre_day)
# pool = pd.read_pickle('/data/group/800442/800319/strategy_local_path/code_list_no688/'+f'{pre_pre_day}.pkl')
# restrict_list = pd.read_pickle(f'{local_config_path}restrict_list.pkl')
# pool = list(set(pool)-set(restrict_list))
# pd.to_pickle(pool,f'{code_list_path}{pre_day}.pkl')

signal_930 = pd.read_pickle(f'{local_config_path}morning_model/val_sign/{date}.pkl')
signal_930 = signal_930.drop(['300362.SZ'])
pd.to_pickle(signal_930,f'{local_config_path}morning_model/val_sign/{date}.pkl')
# pd.to_pickle(pd.Series([]),f'{local_config_path}morning_model/val_sign/{date}.pkl')
