# coding: utf-8
# Author：fengchi863
# Date ：2021/12/20 9:29

import os
import sys
import time
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件')

import itertools
import pandas as pd
from ShortTermTrading.conf.path_conf import junk_path

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

record = list()
# baseline 1.005 -0.01 0.01 0.05 -0.04
for param in sell_cond_param_prod:
    print(param)
    sell_cond_kargs = dict(zip(sell_cond_key_list, param))
    # output_path = junk_path + f'sell_cond_bt_result20210701_20210903/sell_cond_backtest_({param[0]})_({param[1]})_({param[2]})_({param[3]})_({param[4]}).xlsx'
    output_path = junk_path + f'sell_cond_bt_result/sell_cond_backtest_({param[0]})_({param[1]})_({param[2]})_({param[3]})_({param[4]}).xlsx'

    bt_result = pd.read_excel(output_path, sheet_name='逐笔持仓综合统计', index_col=0)
    win_ratio = bt_result.loc['胜率', '全时段']
    per_profit = bt_result.loc['收益率', '全时段']
    profit_and_coss_ratio = bt_result.loc['盈亏比(收益率)', '全时段']
    deal_times = bt_result.loc['交易次数', '全时段'] / 2
    record.append([param[0], param[1], param[2], param[3], param[4],
                   deal_times, per_profit, win_ratio, profit_and_coss_ratio])

ret = pd.DataFrame(record)
ret.columns = ['均线上方容错量', '相比昨收跌幅', '触碰均线反弹力度', 'ma5上方止盈点',
               'ma5下方止损点', '交易笔数', '单笔收益率',
               '胜率', '盈亏比']
# ret.to_excel(junk_path + 'sell_cond_bt_result_summary20210701_20210903.xlsx')
ret.to_excel(junk_path + 'sell_cond_bt_result_summary.xlsx')