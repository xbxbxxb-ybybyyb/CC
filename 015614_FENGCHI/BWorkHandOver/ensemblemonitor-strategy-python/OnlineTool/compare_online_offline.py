# @Time : 2021/4/21 14:47
# @Author : Zhichen Lu
# @File : compare_online_offline.py

import pandas as pd
import numpy as np
from active_pool.simple_tool import get_path_conf
from dataApi.getData import trans_int2windcode
import os


def get_buy_record(date, time_point):
    res = pd.DataFrame(buy_order_record[date][time_point], columns=['stk_id', 'vol', 'deal_price']).set_index('stk_id')
    res.index = pd.MultiIndex.from_tuples([(trans_int2windcode(x), time_point) for x in res.index])
    return res['vol']


def get_sell_record(date, time_point):
    res = pd.DataFrame(sell_order_record[date][time_point], columns=['stk_id', 'sent', 'vol', 'deal_price']).set_index('stk_id').drop('sent', axis=1)
    res.index = pd.MultiIndex.from_tuples([(trans_int2windcode(x), time_point) for x in res.index])
    return res['vol']


date = 20210426
path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
path_conf_sim = get_path_conf('/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim20210426/')
# sell_order_record,buy_order_record = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/validation_file/XGB_Cat_Light_OnlineTestOutSampleRevTriggerFilterHolding_AlphaTriggerPoolTop600_deal_ratio_0.1_per_ratio_0.0050O_buy_sell_order_record.pkl')

buy_order_compare, sell_order_compare = [], []
summary = pd.read_pickle(path_conf['daily_out_path'] + '%d.pkl' % date)
summary_sim = pd.read_pickle(path_conf_sim['daily_out_path'] + '%d.pkl' % date)

for each in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
    offline_buy_signal = summary_sim['buy_order_record'][each]
    online_buy_signal = summary['buy_order_record'][each]
    online_buy_signal.index = pd.MultiIndex.from_tuples([(x, each) for x in online_buy_signal.index])
    offline_buy_signal.index = pd.MultiIndex.from_tuples([(x, each) for x in offline_buy_signal.index])

    offline_sell_signal = summary_sim['sell_order_record'][each]  # get_sell_record(date,time_point=each)
    online_sell_signal = summary['sell_order_record'][each]
    online_sell_signal.index = pd.MultiIndex.from_tuples([(x, each) for x in online_sell_signal.index])
    offline_sell_signal.index = pd.MultiIndex.from_tuples([(x, each) for x in offline_sell_signal.index])

    buy_order_compare.append(pd.DataFrame({'online': online_buy_signal, 'offline': offline_buy_signal}))
    sell_order_compare.append(pd.DataFrame({'online': online_sell_signal, 'offline': offline_sell_signal}))

buy_order_compare = pd.concat(buy_order_compare)
sell_order_compare = pd.concat(sell_order_compare)

buy_record_different = buy_order_compare[buy_order_compare.count(axis=1) < 2]
sell_record_different = sell_order_compare[sell_order_compare.count(axis=1) < 2]


holding_online = pd.read_pickle(path_conf['holding_info_path']+'%d.pkl'%date)
holding_sim = pd.read_pickle(path_conf_sim['holding_info_path']+'%d.pkl'%date)
check = set(holding_online.keys()) - set(holding_sim.keys())
check