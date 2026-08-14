# @Time : 2021/9/12 12:18
# @Author : Zhichen Lu
# @File : barly_compare.py

import pandas as pd
import numpy as np
import os
from ExtraTools import get_path_conf
offline_base_dir =  '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪_BeforeRay/'
from dataApi.sendInfo import send_file
# from online_conf import code_list_path, local_config_path
path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForMix20210803_V20210907/')
local_config_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path = [path_conf[x] for x in\
                                                'local_config_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path'.split(',')]

offline_holding_series = pd.read_pickle(f'{offline_base_dir}record/holding_series_XGB_Cat_Light_OnlineTestOutSampleRevTriggerFilterHolding_AlphaTriggerPoolTop600_deal_ratio_0.1_per_ratio_0.0050OnlineTracing.pkl')
date_list = sorted(list(set([x[0] for x in offline_holding_series])))
bar_list = sorted(list(set([x[1] for x in offline_holding_series])))

stat = {}
for date in date_list:
    # summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    # holding_info = summary['barly_holding_info']
    for bar in bar_list:
        temp_summary = pd.read_pickle(f'{daily_out_path}{date}/{bar}_summary.pkl')
        online_holidng = temp_summary['barly_holding_info'].set_index('Symbol')['NetPosition']
        online_holidng = online_holidng[online_holidng>0]
        online_holidng.index = online_holidng.index.map(lambda x : int(x[:-3]))
        offline_holding = offline_holding_series[(date,bar)].copy()
        offline_cash = offline_holding.pop('init_cash')
        temp_stat = pd.Series({'线上数量':len(online_holidng),'线下数量':len(offline_holding),
                               '线上线下交集':len(set(online_holidng.index).intersection(list(offline_holding.keys()))),
                               '线上现金':temp_summary['bar_inital_cash'],'线下现金':offline_cash})
        temp_stat['交集占线上比例'] = temp_stat['线上线下交集']/temp_stat['线上数量']
        temp_stat['交集占线下比例'] = temp_stat['线上线下交集']/temp_stat['线下数量']
        stat[(date,bar)] = temp_stat
stat = pd.DataFrame(stat).T





        # offline_holding