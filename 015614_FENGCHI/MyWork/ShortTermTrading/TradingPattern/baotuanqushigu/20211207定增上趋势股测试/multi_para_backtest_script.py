# coding: utf-8
# Author：fengchi863
# Date ：2021/12/10 21:12

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试')

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import send_message
root_path = junk_path + 'trend_test/'
import pandas as pd
from generate_daily_stock import wrapper
from backtest import start_backtest
from tqdm import tqdm
import time
import os

everyday_stock_num_baseline = 237
summary = pd.read_excel(root_path + 'summary.xlsx')
# summary = summary.query('380 < 日均趋势个股数量 < 400')
summary = summary.query('480 < 日均趋势个股数量 < 550')
t1 = time.time()
for idx in tqdm(range(len(summary))):
    tmp_row = summary.iloc[idx]
    ma_type = tmp_row['均线排列类型']
    ma_score_60d = tmp_row['60日均线得分']
    ma_score_120d = tmp_row['120日均线得分']
    dis60 = tmp_row['60日均线距离']
    ma_pct = tmp_row['20日内满足ma5<ma20的比例']
    everyday_stock_num = tmp_row['日均趋势个股数量']
    print([ma_type, ma_score_60d, ma_score_120d, dis60, ma_pct, everyday_stock_num])

    output_path = junk_path + f'trend_test_backtest/pp_bt_result_ma({ma_type})_score60d({ma_score_60d})_' \
        f'score120d({ma_score_120d})_' \
        f'trend_dis60({dis60})_pct({ma_pct})_everyday({everyday_stock_num}).xlsx'
    if os.path.exists(output_path):
        continue

    start_date = 20200101
    end_date = 20211201
    file_path = root_path + f'ma({ma_type})_score60d({ma_score_60d})_score120d({ma_score_120d})_' \
        f'trend_dis60({dis60})_pct({ma_pct}).xlsx'
    trend_stock = pd.read_excel(file_path)
    trend_stock['flag'] = True
    trend_stock = trend_stock.pivot(index='mddate', columns='level_1', values='flag').fillna(False)
    trend_stock = trend_stock.loc[start_date:end_date]
    ret_stock = wrapper(start_date, end_date, trend_stock)

    start_backtest(start_date, end_date, ret_stock, output_path)
send_message(['015614'], '多参数回测已完成，用时%ds' % (time.time() - t1))
