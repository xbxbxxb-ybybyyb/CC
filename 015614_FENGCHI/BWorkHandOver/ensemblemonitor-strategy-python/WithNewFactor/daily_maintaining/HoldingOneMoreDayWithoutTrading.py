# @Time : 2021/10/5 22:20
# @Author : Zhichen Lu
# @File : HoldingOneMoreDayWithoutTrading.py

import numpy as np
import pandas as pd
from ExtraTools import get_path_conf
from dataApi.tradeDate import get_pre_trade_date
import shutil




def holidng_one_more_day(date,path_conf,change_buy_time = False):
    local_config_path, daily_out_path, holding_info_path, buy_time_info_path, init_conf_path, path_for_930, sub_output_path, ratio_path = \
        [path_conf[x] for x in
         ['local_config_path', 'daily_out_path', 'holding_info_path', 'buy_time_info_path', 'init_conf_path', 'path_for_930', 'sub_output_path', 'ratio_path']]
    pre_date = get_pre_trade_date(date)
    next_day = get_pre_trade_date(date,-1)
    shutil.copy(f'{holding_info_path}{pre_date}.pkl',f'{holding_info_path}{date}.pkl')
    if change_buy_time:
        pass
    else:
        shutil.copy(f'{buy_time_info_path}{pre_date}.pkl',f'{buy_time_info_path}{date}.pkl')

    shutil.copy(f'{path_for_930}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl',
                f'{path_for_930}{date}/StrategyOut/buy_time_info{date}.pkl')

    shutil.copy(f'{path_for_930}{pre_date}/StrategyOut/holding{pre_date}.pkl',
                f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')

