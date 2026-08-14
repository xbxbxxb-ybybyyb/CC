# @Time : 2021/5/10 7:37
# @Author : Zhichen Lu
# @File : offline_daily_update_for_930.py
import pandas as pd
import datetime,os
from conf.path_config import deal_price_path
from ExtraTools import get_path_conf
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date,get_date_range
import shutil

path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
path_for_930,code_list_path = path_conf['path_for_930'],path_conf['code_list_path']

def get_vol_info(date):
    next_day = get_pre_trade_date(date,-1)
    vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    vol_info.columns = vol_info.columns.map(trans_int2windcode)
    if date not in vol_info.index:
        raise Exception(f'Vol info of 930 are not update in date {date}')
    if not os.path.exists(f'{path_for_930}{next_day}/'):
        os.mkdir(f'{path_for_930}{next_day}/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyIn/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyOut/')
    pd.to_pickle(vol_info.loc[(date,930)].fillna(0),f'{path_for_930}{next_day}/StrategyIn/vol_info{next_day}.pkl')

# get_vol_info(20210511)
# for date in get_date_range(20210301,20210330):
    # shutil.copy(f'/data/group/800319/strategy_local_path/code_list_no688/{date}.pkl',f'{code_list_path}{date}.pkl')
    # get_vol_info(date)
#     print(date)

