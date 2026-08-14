# coding: utf-8
# Author：fengchi863
# Date ：2021/12/23 14:04

import os
import sys
import time
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211222刻画10日均线选股及买卖点测试')

from backtest import start_backtest
import pandas as pd
from ShortTermTrading.conf.path_conf import junk_path

trend_stock = pd.read_pickle(junk_path + 'trend_daily_stock_ma10_20211222.pkl')

# output_path = junk_path + f'sell_cond_backtest_ma10_20210101_20211131.xlsx'
output_path = junk_path + f'sell_cond_backtest_ma10_20210701_20210903.xlsx'
# start_backtest(20210701, 20210903, trend_stock, output_path, mode='multi')
start_backtest(20210701, 20210903, trend_stock[[830, 831]], output_path, mode='serial')  # debug
# start_backtest(20210101, 20211131, trend_stock, output_path, mode='multi')
