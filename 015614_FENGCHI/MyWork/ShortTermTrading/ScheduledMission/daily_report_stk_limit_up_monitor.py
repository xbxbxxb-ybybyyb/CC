# coding: utf-8
# Author：fengchi863
# Date ：2021/3/11 16:46

import sys
sys.path.append('/data/group/800319')
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')

from ShortTermTrading.Util.tools import load_pickle, get_today_date, get_curr_datetime, send_message
from ShortTermTrading.Util.System import get_stock_name_dict
from ShortTermTrading.conf.path_conf import report_monitor_output_path
from xquant.thirdpartydata.marketdata import MarketData
from ShortTermTrading.dataApi import stockList
import time
import pandas as pd

stk_code_name_dict = get_stock_name_dict()

def generate_link_message(stk_code, reversed_df):
    if type(stk_code) == int:
        stk_code = stockList.trans_int2windcode(stk_code)

    report_types = reversed_df[reversed_df['stk_code'] == stk_code].index.tolist()

    for report_type in report_types:
        if report_type == '季报跟踪':
            str0 = '##########\n'
            str1 = '隔夜一季报预告发布盘中涨停监控\n'
            stock_name = stk_code_name_dict[stk_code] if stockList.trans_int2windcode(stk_code) in stk_code_name_dict.keys() else stk_code
            str2 = stock_name + '涨停'
            return str0 + str1 + str2
        if report_type == '年报业绩快报跟踪':
            str0 = '##########\n'
            str1 = '年报业绩快报盘中涨停监控\n'
            stock_name = stk_code_name_dict[stk_code] if stockList.trans_int2windcode(
                stk_code) in stk_code_name_dict.keys() else stk_code
            str2 = stock_name + '涨停'
            return str0 + str1 + str2
        if report_type == '年报报告跟踪':
            str0 = '##########\n'
            str1 = '年报报告发布盘中涨停监控\n'
            stock_name = stk_code_name_dict[stk_code] if stockList.trans_int2windcode(
                stk_code) in stk_code_name_dict.keys() else stk_code
            str2 = stock_name + '涨停'
            return str0 + str1 + str2

def start_intra_limit_judge(monitor_dict):
    ma = MarketData()

    # 解析monitor_dict
    reversed_df = pd.DataFrame()
    for key in monitor_dict:
        tmp_df = pd.DataFrame(monitor_dict[key], index=[key] * len(monitor_dict[key]), columns=['stk_code'])
        reversed_df = pd.concat([reversed_df, tmp_df], axis=0)

    monitor_list = []
    for key in monitor_dict:
        monitor_list += monitor_dict[key]

    now_date = get_today_date()
    now_start_datetime = now_date * 1000000 + 90000
    now_end_datetime = now_date * 1000000 + 150000
    triggered_list = []  # 记录当天已经触发过的个股
    while (True):
        for stk_id in monitor_list:
            time.sleep(1)  # 防止频繁调用
            stk_code = stockList.trans_int2windcode(stk_id)
            now_mddatetime = get_curr_datetime()
            print('===========================================')
            print('当前时间：', now_mddatetime)
            if now_mddatetime < 93000:
                continue
            # 实时横截面数据
            df1 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=101, securityType=2)
            df2 = ma.getMDSecurityRecordBySourceTypes(securityIDSource=102, securityType=2)
            cross_info = df1.append(df2)
            cross_info = cross_info.set_index('HTSCSecurityID', drop=True)
            pre_close = cross_info.at[stk_code, 'PreClosePx']

            stk_code = stockList.trans_int2windcode(stk_id)
            time.sleep(0.1)
            md_kline_df = ma.getMDSecurityKLineDataFrame(stk_code, str(now_start_datetime), \
                                                         str(now_end_datetime), 10, 20)
            if len(md_kline_df) == 0:
                continue

            minute_latest_info = md_kline_df.iloc[-1]
            latest_close_px = minute_latest_info['ClosePx']
            latest_pctchg = latest_close_px / pre_close - 1

            if ((not stk_code.startswith('3')) and latest_pctchg > 0.098) | \
                (stk_code.startswith('3') and latest_pctchg > 0.198):
                if stk_code not in triggered_list:
                    link_message = generate_link_message(stk_code, reversed_df)
                    triggered_list.append(stk_code)
                    send_message(['fengchi', '003186', '011669', '011670', '015628', '015630', '003376', '015624'], link_message)
        if now_mddatetime > 150100:
            print('当天监控结束')
            break

if __name__ == '__main__':
    # 记录运行时间
    today_date = get_today_date()
    monitor_dict = load_pickle(report_monitor_output_path + '监控股票池%d.pkl' % today_date)
    start_intra_limit_judge(monitor_dict)
