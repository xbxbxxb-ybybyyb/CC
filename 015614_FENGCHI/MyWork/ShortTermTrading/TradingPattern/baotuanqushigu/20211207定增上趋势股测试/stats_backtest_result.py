# coding: utf-8
# Author：fengchi863
# Date ：2021/12/13 14:49

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试')

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import send_message
root_path = junk_path + 'trend_test/'
backtest_root_path = junk_path + 'trend_test_backtest/'
import pandas as pd
from tqdm import tqdm
from check_trend_ma_arrange import ma_types
import time

everyday_stock_num_baseline = 237
summary = pd.read_excel(root_path + 'summary.xlsx')
summary1 = summary.query('380 < 日均趋势个股数量 < 400')
summary2 = summary.query('480 < 日均趋势个股数量 < 550')
summary = pd.concat([summary1, summary2])

record = list()
for idx in tqdm(range(len(summary))):
    tmp_row = summary.iloc[idx]
    ma_type = tmp_row['均线排列类型']
    ma_score_60d = tmp_row['60日均线得分']
    ma_score_120d = tmp_row['120日均线得分']
    dis60 = tmp_row['60日均线距离']
    ma_pct = tmp_row['20日内满足ma5<ma20的比例']
    everyday_stock_num = tmp_row['日均趋势个股数量']

    output_path = junk_path + f'trend_test_backtest/pp_bt_result_ma({ma_type})_score60d({ma_score_60d})_' \
                              f'score120d({ma_score_120d})_' \
        f'trend_dis60({dis60})_pct({ma_pct})_everyday({everyday_stock_num}).xlsx'

    bt_result = pd.read_excel(output_path, sheet_name='逐笔持仓综合统计', index_col=0)
    win_ratio = bt_result.loc['胜率', '全时段']
    per_profit = bt_result.loc['收益率', '全时段']
    profit_and_coss_ratio = bt_result.loc['盈亏比(收益率)', '全时段']
    deal_times = bt_result.loc['交易次数', '全时段'] / 2
    record.append([ma_type, ma_score_60d, ma_score_120d, dis60, ma_pct, everyday_stock_num,
                   deal_times, per_profit, win_ratio, profit_and_coss_ratio])
ret = pd.DataFrame(record)
ret.columns = ['均线排列类型', '60日均线得分', '120日均线得分', '60日均线距离',
               '20日内满足ma5<ma20的比例', '日均趋势个股数量', '交易笔数', '单笔收益率',
               '胜率', '盈亏比']
ret['均线排列详细类型'] = ret['均线排列类型'].apply(lambda x: ma_types[x])
ret.to_excel(junk_path + 'backtest_summary.xlsx')
