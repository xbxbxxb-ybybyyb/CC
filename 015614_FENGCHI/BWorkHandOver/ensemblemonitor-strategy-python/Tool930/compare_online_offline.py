# @Time : 2021/5/7 15:00
# @Author : Zhichen Lu
# @File : compare_online_offline.py

import pandas as pd
# from online_conf import local_config_path,sub_output_path,path_for_930
from ExtraTools import get_path_conf
from dataApi.getData import trans_windcode2int,get_daily_1factor
from dataApi.tradeDate import get_pre_trade_date
import os
path_conf = get_path_conf('/data/group/800319/strategy_local_path3_for_930/')

local_config_path,sub_output_path,path_for_930 = [path_conf[x] for x in ['local_config_path','sub_output_path','path_for_930']]

daily_holding, daily_buy_time_info, daily_conf = pd.read_pickle('/data/group/800319/strategy_local_path/FolderFor930/fake_sample_new_frame_out_sample.pkl')

holding_compare = {}

for date in sorted(list(daily_holding)):
    if not os.path.exists(f'{sub_output_path}{date}.pkl'):
        break
    next_day = get_pre_trade_date(date,-1)
    summary = pd.read_pickle(f'{sub_output_path}{date}.pkl')
    online_holding = summary['barly_holding_info'][1000].set_index('Symbol')['NetPosition']
    online_holding = online_holding[online_holding>0]
    online_holding.index = online_holding.index.map(trans_windcode2int)
    offline_holding = pd.Series(daily_holding[date])
    close = get_daily_1factor('close',date_list=[date],code_list=offline_holding.index.tolist()).loc[date]
    online_next_day_initial = pd.read_pickle(f'{path_for_930}{next_day}/StrategyIn/account_info{next_day}.pkl')
    # offline_holding.index = offline_holding.index.map(trans_int2windcode)
    intersect_stk =list( set(online_holding.index).intersection(offline_holding.index))
    temp_holding_stat = {'线上持仓数量':len(online_holding),'线下持仓数量':len(offline_holding),
                         '线上线下持仓交集数量':len(intersect_stk),
                         '线上线下持仓数量一致股票数':(online_holding.loc[intersect_stk]==offline_holding.loc[intersect_stk]).sum(),
                         '线上账户总规模':online_next_day_initial['account_value'],
                        '线下账户总规模':(offline_holding * close).sum()+daily_conf[next_day]['cash']}
    holding_compare[date] = pd.Series(temp_holding_stat)

holding_compare = pd.DataFrame(holding_compare).T
