# coding: utf-8
# Author：fengchi863
# Date ：2023/7/3 18:46

"""
添加新策略的成交记录经验：
模仿一个类似的策略， 主要新增1.sell 以及 3.buy
最后运行第一天时，需要创建一个前一天的空的卖出记录，买入记录，因子模型对比记录（使用UAT的直接改成prod即可）

5-5系列，有些图会没有
"""
import pandas as pd
import datetime as dt
import sys
import os
import time
from xquant.factordata import FactorData
s = FactorData()
from LucienUtil.FileUtil import FileUtil
from dataApi.sendInfo import send_message

cpp_path = '/data/group/800463/日内强势股/cpp_log_parse/'
saturn_path = '/data/group/800463/日内强势股/saturn_log_parse/'
sell_path = '/data/group/800463/日内强势股/sell_log_parse/'
leda_path = '/data/group/800463/日内强势股/leda_log_parse/'
jupiter_path = '/data/group/800463/日内强势股/jupiter_log_parse/'    # 202040704上线
output_path = '/data/group/800463/日内强势股/log_parse/'

cpp_record_path = '/data/group/800463/日内强势股/cpp_实盘分析记录/'
saturn_record_path = '/data/group/800463/日内强势股/saturn_log_parse/'
jupiter_record_path = '/data/group/800463/日内强势股/jupiter_log_parse/'
sell_record_path = '/data/group/800463/日内强势股/sell_实盘分析记录/'
leda_record_path = '/data/group/800463/日内强势股/leda_log_parse/'

output_record_path = '/data/group/800463/日内强势股/实盘分析记录/'

enviroment_list = ['prod']

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
    # date = '20240429' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('current date = %s' % date)
today_date_str = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
today_date = date

for envir in enviroment_list:
    # ------------------------------------------------------
    # 拼接因子耗时文件

    cpp_log_parse_fpath = cpp_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'
    jupiter_log_parse_fpath = jupiter_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'
    saturn_log_parse_fpath = saturn_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'
    sell_log_parse_fpath = sell_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'
    leda_log_parse_fpath = leda_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'

    while not os.path.exists(cpp_log_parse_fpath):
        send_message(f'{today_date} cpp因子耗时文件缺失')
        time.sleep(30)
    while not os.path.exists(jupiter_log_parse_fpath):
        send_message(f'{today_date} jupiter因子耗时文件缺失')
        time.sleep(30)
    while not os.path.exists(saturn_log_parse_fpath):
        send_message(f'{today_date} saturn因子耗时文件缺失')
        time.sleep(30)
    while not os.path.exists(sell_log_parse_fpath):
        send_message(f'{today_date} sell因子耗时文件缺失')
        time.sleep(30)
    while not os.path.exists(leda_log_parse_fpath):
        send_message(f'{today_date} leda因子耗时文件缺失')
        time.sleep(30)

    total_factor_cost_df_dict = dict()
    cpp_factor_cost_df_dict = pd.read_excel(cpp_log_parse_fpath, sheet_name=None, index_col=0)
    jupiter_factor_cost_df_dict = pd.read_excel(jupiter_log_parse_fpath, sheet_name=None, index_col=0)
    saturn_factor_cost_df = pd.read_excel(saturn_log_parse_fpath, sheet_name='因子耗时Saturn', index_col=0)
    sell_factor_cost_df_dict = pd.read_excel(sell_log_parse_fpath, sheet_name=None, index_col=0)
    leda_factor_cost_df_dict = pd.read_excel(leda_log_parse_fpath, sheet_name=None, index_col=0)

    total_factor_cost_df_dict['因子耗时'] = jupiter_factor_cost_df_dict['因子耗时']
    total_factor_cost_df_dict['因子耗时New'] = cpp_factor_cost_df_dict['因子耗时New']
    total_factor_cost_df_dict['Leda样本'] = leda_factor_cost_df_dict['因子耗时']
    total_factor_cost_df_dict['项目二931样本'] = saturn_factor_cost_df
    total_factor_cost_df_dict['项目二930样本'] = pd.DataFrame()
    total_factor_cost_df_dict['Ceres931样本'] = pd.DataFrame()
    total_factor_cost_df_dict['Sell1样本'] = sell_factor_cost_df_dict['Sell1样本']
    total_factor_cost_df_dict['Sell3样本'] = sell_factor_cost_df_dict['Sell3样本']

    FileUtil.save_dict2xls(total_factor_cost_df_dict, output_path + '因子耗时/', f'因子耗时_{today_date_str}_{envir}.xlsx')

    # ------------------------------------------------------
    ## 拼接每日突破文件
    saturn_tupo_df_dict = pd.read_excel(saturn_record_path + f'每日突破/每日突破_{today_date}_{envir}.xlsx', sheet_name=None, index_col=0)
    jupiter_tupo_df_dict = pd.read_excel(jupiter_record_path + f'每日突破/每日突破_{today_date}_{envir}.xlsx', sheet_name=None, index_col=0)
    leda_tupo_df_dict = pd.read_excel(leda_record_path + f'每日突破/每日突破_{today_date}_{envir}.xlsx', sheet_name=None, index_col=0)
    cpp_tupo_df_dict = pd.read_excel(cpp_record_path + f'每日突破/每日突破_{today_date}_{envir}.xlsx', sheet_name=None, index_col=0)

    ## 每日订单
    saturn_deal = saturn_tupo_df_dict['每日订单']
    leda_deal = leda_tupo_df_dict['每日订单']
    eur_deal = cpp_tupo_df_dict['每日订单']
    jup_deal = jupiter_tupo_df_dict['每日订单']
    cpp_tupo_df_dict['每日订单'] = pd.concat([saturn_deal, eur_deal, jup_deal, leda_deal], axis=0)

    ## 每日突破
    cpp_tupo_df_dict['每日项目二'] = saturn_tupo_df_dict['每日突破Saturn']
    cpp_tupo_df_dict['每日突破Leda'] = leda_tupo_df_dict['每日突破']
    cpp_tupo_df_dict['每日突破'] = jupiter_tupo_df_dict['每日突破']
    cpp_tupo_df_dict['每日突破New'] = cpp_tupo_df_dict['每日突破New']

    ## 每日拒绝
    saturn_reject = saturn_tupo_df_dict['每日拒绝']
    leda_reject = leda_tupo_df_dict['每日拒绝']
    cpp_reject = cpp_tupo_df_dict['每日拒绝']
    jupiter_reject = jupiter_tupo_df_dict['每日拒绝']
    if len(saturn_reject) != 0 or len(leda_reject) != 0 or len(jupiter_reject) != 0:
        concat = pd.concat([cpp_reject, leda_reject, saturn_reject, jupiter_reject], axis=0)
    else:
        concat = cpp_reject
    cpp_tupo_df_dict['每日拒绝'] = concat

    FileUtil.save_dict2xls(cpp_tupo_df_dict, output_record_path + '每日突破/', f'每日突破_{today_date}_{envir}.xlsx')
