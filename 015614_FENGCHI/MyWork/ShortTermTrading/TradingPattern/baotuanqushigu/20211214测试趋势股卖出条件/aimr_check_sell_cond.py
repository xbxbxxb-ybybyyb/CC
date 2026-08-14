# coding: utf-8
# Author：fengchi863
# Date ：2021/12/16 15:29

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件')

from backtest import start_backtest
import itertools
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import junk_path
from xquant.compute.aimr import AIMR
import os


def divide(lst, slice_num):
    size = len(lst) // slice_num + 1
    if size <= 0:
        return [lst]
    ret = [lst[i * size:(i+1)*size] for i in range(0, np.ceil(len(lst)/size))]
    for i in range(np.array(ret).shape[0]):
        print(len(ret[i]), end=' ')


if __name__ == '__main__':
    param = AIMR.getParam()
    param = int(param)

    trend_stock = pd.read_pickle(junk_path + 'trend_daily_stock_20211215_oldVersion.pkl')

    sell_cond_dict = {
        '均线上方容错量': [1.005, 1.1],
        '相比昨收跌幅': [-0.02, -0.01, 0],
        '触碰均线反弹力度': [0.005, 0.01, 0.015, 0.02],
        'ma5上方止盈点': [0.04, 0.05, 0.06, 0.07],
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
        output_path = junk_path + f'sell_cond_bt_result20210701_20210903/sell_cond_backtest_({param[0]})_({param[1]})_({param[2]})_({param[3]})_({param[4]}).xlsx'
        if os.path.exists(output_path):
            remove_list.append(param)
    sell_cond_param_prod = list(set(sell_cond_param_prod) - set(remove_list))

    length = len(sell_cond_param_prod)
    part = int(length / 10)
    start = (param - 1) * part
    end = param * part
    if param == 4:
        end = length
    print(start, end)

    for param in sell_cond_param_prod[start: end]:
        sell_cond_kargs = dict(zip(sell_cond_key_list, param))
        output_path = junk_path + f'sell_cond_bt_result20210701_20210903/sell_cond_backtest_({param[0]})_({param[1]})_({param[2]})_({param[3]})_({param[4]}).xlsx'
        start_backtest(20210701, 20210903, trend_stock, output_path, **sell_cond_kargs)
