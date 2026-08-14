# coding: utf-8
# Author：fengchi863
# Date ：2021/12/15 14:14

import os
import sys
import time
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件')

from v2_backtest import start_backtest
import itertools
import pandas as pd
from ShortTermTrading.conf.path_conf import junk_path

# sell_cond_kargs = {
#     '高位回调涨幅参数': [0.05, 0.06, 0.07],
#     '高位回调回撤参数': [0.01, 0.02, 0.03],
#     '超越5日线涨跌幅止盈参数': [],
#     '低于5日线涨跌幅止损参数': [],
# }

# sell_cond_args = ['日内高位回调止盈卖出',
#                   '超越5日线止盈卖出']
# prod_enum = [(1, 0), (0, 1)]

sell_cond_dict = {
    '均线上方容错量': [1.005, 1.1],
    '相比昨收跌幅': [-0.02, -0.01, 0],
    '触碰均线反弹力度': [0.005, 0.01],
    'MA5上方监测点参数': [0.05, 0.06, 0.07],
    'MA5上方回撤参数': [-0.01, -0.02],
    'ma5下方止损点': [-0.05, -0.04, -0.03]
}

sell_cond_key_list = list(sell_cond_dict.keys())
sell_cond_param_list = list()
for sell_cond_key in sell_cond_key_list:
     sell_cond_param_list.append(sell_cond_dict[sell_cond_key])
sell_cond_param_prod = list(itertools.product(*sell_cond_param_list))

remove_list = list()
for param in sell_cond_param_prod:
    sell_cond_kargs = dict(zip(sell_cond_key_list, param))
    output_path = junk_path + f'sell_cond2_bt_result20210701_20210903/sell_cond_backtest_({param[0]})_({param[1]})_({param[2]})_({param[3]})_({param[4]}).xlsx'
    if os.path.exists(output_path):
        remove_list.append(param)
sell_cond_param_prod = list(set(sell_cond_param_prod) - set(remove_list))

trend_stock = pd.read_pickle(junk_path + 'trend_daily_stock_20211215_oldVersion.pkl')

for param in sell_cond_param_prod:
    print(param)
    sell_cond_kargs = dict(zip(sell_cond_key_list, param))
    output_path = junk_path + f'sell_cond2_bt_result/sell_cond_backtest_({param[0]})_({param[1]})_({param[2]})_({param[3]})_({param[4]}).xlsx'
    start_backtest(20210101, 20211130, trend_stock, output_path, **sell_cond_kargs)




