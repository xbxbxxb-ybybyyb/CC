# @Time : 2021/5/11 21:38
# @Author : Zhichen Lu
# @File : daily_update_pre_night.py
import sys

sys.path.extend(
    ['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python',
     '/data/user/015664/TriggeredTrading/StrongStockModel',
     '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
     '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
     '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training',
     '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

import pandas as pd
import datetime, os
from StrongStockModel.conf.path_config import deal_price_path
from ExtraTools import get_path_conf
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_pre_trade_date, get_date_range, get_recent_trade_date
import shutil, datetime
from dataApi.sendInfo import send_message


# path_conf = get_path_conf('/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim20210513/')


def get_vol_info(date):
    next_day = get_pre_trade_date(date, -1)
    vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    vol_info.columns = vol_info.columns.map(trans_int2windcode)
    if date not in vol_info.index:
        raise Exception(f'Vol info of 930 are not update in date {date}')
    if not os.path.exists(f'{path_for_930}{next_day}/'):
        os.mkdir(f'{path_for_930}{next_day}/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyIn/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyOut/')
    pd.to_pickle(vol_info.loc[(date, 930)].fillna(0), f'{path_for_930}{next_day}/StrategyIn/vol_info{next_day}.pkl')


def calc_two_part_ratio(date):
    holding_7_bar = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding_930_bar = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    compare = pd.DataFrame({'bar_930': pd.Series(holding_930_bar), 'bar_7': pd.Series(holding_7_bar)}).fillna(0)
    ratio = (compare.T / compare.sum(axis=1)).T
    if not os.path.exists(ratio_path):
        os.mkdir(ratio_path)
    print(ratio.sort_values('bar_930'))
    pd.to_pickle(ratio.drop('cash'), f'{ratio_path}{date}.pkl')


def out_factor_list(today):
    date = get_pre_trade_date(today, -1)
    local_config_path = f'/data/group/800319/strategy_local_path3_ForMatrix/'
    # min5_factor_list = pd.read_pickle(f'{local_config_path}using_5min_list.pkl')
    all_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor3/20210722/DateCode/factor_list.pkl')
    # all_desample_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor3/20210722/DateCode/desample_factor_list.pkl')

    fix_factor_list = list(map(lambda x: x.replace('.npy', ''),
                               os.listdir(
                                   '/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/')))  # pd.read_pickle('/data/group/800319/strategy_local_path_file/available_factor_list.pkl')
    fix_factor_list = list(set(fix_factor_list) - set(['idx_date', 'idx_code', 'idx_time', 'nolimit', 'future']))
    fix_factor_list = list(filter(lambda x: x.startswith('M5'), fix_factor_list))
    # all_desample_factor_list = fix_factor_list

    # filtered_min5_factor = list(filter(lambda x : not x.startswith('M5'),min5_factor_list))
    # desample_factor_list = list(filter(lambda x : x.startswith('M5'),min5_factor_list))

    desample_factor_list = fix_factor_list  # list(filter(lambda x : x[0] in desample_factor_list,all_desample_factor_list))
    filtered_min5_factor = list(filter(lambda x: x[0] in filtered_min5_factor, all_factor_list))

    pd.to_pickle(filtered_min5_factor, f'/data/group/800442/800319/strategy_HFfactor/subscript_factor_list/factor_list{date}.pkl')
    pd.to_pickle(desample_factor_list, f'/data/group/800442/800319/strategy_HFfactor/subscript_factor_list/desample_factor_list{date}.pkl')


if __name__ == '__main__':
    today = get_pre_trade_date()
    path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForMatrix/')
    path_for_930, code_list_path, holding_info_path, ratio_path = [path_conf[x] for x in 'path_for_930,code_list_path,holding_info_path,ratio_path'.split(',')]
    get_vol_info(today)
    calc_two_part_ratio(today)
    send_message(['015664'], '仿真930成交量及ratio更新完成')
    out_factor_list(today=today)

local_path = '/data/group/800442/800319/strategy_HFfactor/'
date_list = sorted(os.listdir('/data/group/800442/800319/strategy_HFfactor/'))
for date in date_list:
    check = pd.read_pickle(f'{local_path}{20211214}/DateCode/desample_factor_list.pkl')
    print(date, len(check))
