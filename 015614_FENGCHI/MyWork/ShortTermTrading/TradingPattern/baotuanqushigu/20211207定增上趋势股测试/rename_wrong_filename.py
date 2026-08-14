# coding: utf-8
# Author：fengchi863
# Date ：2021/12/13 15:37

'''
临时任务已运行完成，作废
'''

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import send_message
root_path = junk_path + 'trend_test/'
bt_root_path = junk_path + 'trend_test_backtest'
bt_root_path2 = junk_path + 'trend_test_backtest2'
import pandas as pd
from generate_daily_stock import wrapper
from backtest import start_backtest
from tqdm import tqdm
import time
import os
import shutil

everyday_stock_num_baseline = 237
summary = pd.read_excel(root_path + 'summary.xlsx')
# summary = summary.query('380 < 日均趋势个股数量 < 400')
summary = summary.query('480 < 日均趋势个股数量 < 550')

have_bt_name = os.listdir(bt_root_path)

for idx in tqdm(range(len(summary))):
    tmp_row = summary.iloc[idx]
    ma_type = tmp_row['均线排列类型']
    ma_score_60d = tmp_row['60日均线得分']
    ma_score_120d = tmp_row['120日均线得分']
    dis60 = tmp_row['60日均线距离']
    ma_pct = tmp_row['20日内满足ma5<ma20的比例']
    everyday_stock_num = tmp_row['日均趋势个股数量']

    filename = list(filter(lambda x: str(everyday_stock_num) in x, have_bt_name))
    old_output_path = junk_path + 'trend_test_backtest/pp_bt_result_ma({ma_type})_score60d({ma_score_60d})_' \
        'score120d({ma_score_120d})_' \
        f'trend_dis60({dis60})_pct({ma_pct}_everyday{everyday_stock_num}).xlsx'
    if not os.path.exists(old_output_path):
        continue
    new_output_path = junk_path + f'trend_test_backtest2/pp_bt_result_ma({ma_type})_score60d({ma_score_60d})_' \
        f'score120d({ma_score_120d})_' \
        f'trend_dis60({dis60})_pct({ma_pct})_everyday({everyday_stock_num}).xlsx'
    shutil.copyfile(old_output_path, new_output_path)
