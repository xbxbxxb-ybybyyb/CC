# coding: utf-8
# Author：fengchi863
# Date ：2023/7/3 18:46

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
output_path = '/data/group/800463/日内强势股/log_parse/'

cpp_record_path = '/data/group/800463/日内强势股/cpp_实盘分析记录/'
saturn_record_path = '/data/group/800463/日内强势股/saturn_log_parse/'
sell_record_path = '/data/group/800463/日内强势股/sell_实盘分析记录/'

output_record_path = '/data/group/800463/日内强势股/实盘分析记录/'

enviroment_list = ['prod']

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
    date = '20240401' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('current date = %s' % date)
today_date_str = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
today_date = date

for envir in enviroment_list:
    # ------------------------------------------------------
    # 拼接因子耗时文件

    cpp_log_parse_fpath = cpp_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'
    saturn_log_parse_fpath = saturn_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'
    sell_log_parse_fpath = sell_path + f'因子耗时/因子耗时_{today_date_str}_{envir}.xlsx'

    while not os.path.exists(cpp_log_parse_fpath):
        send_message(f'{today_date} cpp因子耗时文件缺失')
        time.sleep(30)
    while not os.path.exists(saturn_log_parse_fpath):
        send_message(f'{today_date} saturn因子耗时文件缺失')
        time.sleep(30)
    while not os.path.exists(sell_log_parse_fpath):
        send_message(f'{today_date} saturn因子耗时文件缺失')
        time.sleep(30)

    total_factor_cost_df_dict = dict()
    cpp_factor_cost_df_dict = pd.read_excel(cpp_log_parse_fpath, sheet_name=None, index_col=0)
    saturn_factor_cost_df = pd.read_excel(saturn_log_parse_fpath, sheet_name='因子耗时Saturn', index_col=0)
    sell_factor_cost_df_dict = pd.read_excel(sell_log_parse_fpath, sheet_name=None, index_col=0)

    total_factor_cost_df_dict['因子耗时'] = cpp_factor_cost_df_dict['因子耗时']
    total_factor_cost_df_dict['因子耗时New'] = cpp_factor_cost_df_dict['因子耗时New']
    total_factor_cost_df_dict['项目二931样本'] = saturn_factor_cost_df
    total_factor_cost_df_dict['项目二930样本'] = pd.DataFrame()
    total_factor_cost_df_dict['Ceres931样本'] = pd.DataFrame()
    total_factor_cost_df_dict['Sell1样本'] = sell_factor_cost_df_dict['Sell1样本']
    total_factor_cost_df_dict['Sell3样本'] = sell_factor_cost_df_dict['Sell3样本']

    FileUtil.save_dict2xls(total_factor_cost_df_dict, output_path + '因子耗时/', f'因子耗时_{today_date_str}_{envir}.xlsx')

    # ------------------------------------------------------
    ## 拼接每日突破文件
    saturn_tupo_df_dict = pd.read_excel(saturn_record_path + f'每日突破/每日突破_{today_date}_{envir}.xlsx', sheet_name=None, index_col=0)
    cpp_tupo_df_dict = pd.read_excel(cpp_record_path + f'每日突破/每日突破_{today_date}_{envir}.xlsx', sheet_name=None, index_col=0)

    ## 每日订单
    saturn_deal_jup = saturn_tupo_df_dict['每日订单']
    cpp_deal_jup = cpp_tupo_df_dict['每日订单']
    cpp_tupo_df_dict['每日订单'] = pd.concat([saturn_deal_jup, cpp_deal_jup], axis=0)

    ## 每日突破
    cpp_tupo_df_dict['每日项目二'] = saturn_tupo_df_dict['每日突破Saturn']
    cpp_tupo_df_dict['每日突破'] = cpp_tupo_df_dict['每日突破']
    cpp_tupo_df_dict['每日突破New'] = cpp_tupo_df_dict['每日突破New']

    ## 每日拒绝
    saturn_reject = saturn_tupo_df_dict['每日拒绝']
    cpp_reject = cpp_tupo_df_dict['每日拒绝']
    if len(saturn_reject) != 0:
        concat = pd.concat([cpp_reject, saturn_reject], axis=0)
    else:
        concat = cpp_reject
    cpp_tupo_df_dict['每日拒绝'] = concat

    FileUtil.save_dict2xls(cpp_tupo_df_dict, output_record_path + '每日突破/', f'每日突破_{today_date}_{envir}.xlsx')
