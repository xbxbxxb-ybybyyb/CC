# @Time : 2021/9/16 19:28
# @Author : Zhichen Lu
# @File : generate_day_param.py
import pandas as pd
import os, datetime

loca_path = '/data/group/800442/800319/strategy_HFfactor/'

today = int(datetime.datetime.today().strftime('%Y%m%d'))
param = dict(object_store_memory=50 * (2 ** 30))
if not os.path.exists(f'{loca_path}{today}/'):
    os.makedirs(f'{loca_path}{today}/')
pd.to_pickle(param, f'{loca_path}{today}/ray_param.pkl')
