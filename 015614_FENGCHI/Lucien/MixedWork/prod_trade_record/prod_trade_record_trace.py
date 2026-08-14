# coding: utf-8
# Author：fengchi863
# Date ：2022/9/22 8:49

"""
实盘交易记录每日跟踪
"""
import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import pandas as pd
from xquant.factordata import FactorData
from dataApi.sendInfo import send_message

fd = FactorData()
root_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
today_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
# today_date = 20230214
today_date_str = pd.to_datetime(str(today_date)).strftime('%Y-%m-%d')

def daily_strat_tracking(today_date, today_date_str):
    message = ''
    #%% jupiter策略跟踪
    message += f'jupiter策略{today_date}情况：\n'
    try:
        jupiter_fpath = root_path + 'jupiter成交记录-%s.xlsx' % today_date
        jupiter_today_summary = pd.read_excel(jupiter_fpath, sheet_name='今日汇总情况')
        today_sell_profit = jupiter_today_summary.iloc[20, 1]
        message += f'当日卖出盈利：{round(today_sell_profit, 2)}\n'
        jupiter_buy_record = pd.read_excel(jupiter_fpath, sheet_name='累计买入明细')
        jupiter_buy_record = jupiter_buy_record.query(f'发生日期 >= "{today_date_str}" & 成交金额 > 0')
        message += f'当日买入数量：{len(jupiter_buy_record)}({int(jupiter_buy_record["成交金额"].sum() // 1e4)})\n'
        jupiter_buy_record['message'] = jupiter_buy_record['证券名称'] + '(' + (jupiter_buy_record["成交金额"] // 1e4).map(int).map(str) + ')'
        jupiter_sell_record = pd.read_excel(jupiter_fpath, sheet_name='累计卖出明细')
        jupiter_sell_record = jupiter_sell_record.dropna(subset=['卖出日期'])
        jupiter_sell_record['卖出日期列表'] = jupiter_sell_record['卖出日期'].apply(lambda x: x.split(','))
        jupiter_sell_record = jupiter_sell_record[jupiter_sell_record['卖出日期列表'].apply(lambda x: today_date_str in x)]
        jupiter_sell_record['卖出金额列表'] = jupiter_sell_record['卖出金额'].apply(lambda x: x.split(',') if type(x) == str else [x])
        jupiter_sell_record['卖出金额最后一个'] = jupiter_sell_record['卖出金额列表'].apply(lambda x: str(int(float(x[-1]) // 1e4)))
        message += f'当日卖出总金额：{jupiter_sell_record["卖出金额最后一个"].astype(int).sum()}\n'
        jupiter_sell_record['message'] = jupiter_sell_record['证券名称'] + '(' + jupiter_sell_record["卖出金额最后一个"] + ')'
        message += f'买入：{"，".join(jupiter_buy_record["message"].tolist())}\n'
        message += f'卖出：{"，".join(jupiter_sell_record["message"].tolist())}\n'
        message += '-' * 10 + '\n'
    except:
        message += '***jupiter当日没有数据\n'

    #%% europa策略跟踪
    message += f'europea策略{today_date}情况：\n'
    try:
        europa_fpath = root_path + 'Europa成交记录-%s.xlsx' % today_date
        europa_today_summary = pd.read_excel(europa_fpath, sheet_name='今日汇总情况')
        today_sell_profit = europa_today_summary.iloc[20, 1]
        message += f'当日卖出盈利：{round(today_sell_profit, 2)}\n'
        europa_buy_record = pd.read_excel(europa_fpath, sheet_name='累计买入明细')
        europa_buy_record = europa_buy_record.query(f'发生日期 >= "{today_date_str}" & 成交金额 > 0')
        message += f'当日买入数量：{len(europa_buy_record)}({int(europa_buy_record["成交金额"].sum() // 1e4)})\n'
        europa_buy_record['message'] = europa_buy_record['证券名称'] + '(' + (europa_buy_record["成交金额"] // 1e4).map(int).map(str) + ')'
        europa_sell_record = pd.read_excel(europa_fpath, sheet_name='累计卖出明细')
        europa_sell_record = europa_sell_record.dropna(subset=['卖出日期'])
        europa_sell_record['卖出日期列表'] = europa_sell_record['卖出日期'].apply(lambda x: x.split(','))
        europa_sell_record = europa_sell_record[europa_sell_record['卖出日期列表'].apply(lambda x: today_date_str in x)]
        europa_sell_record['卖出金额列表'] = europa_sell_record['卖出金额'].apply(lambda x: x.split(',') if type(x) == str else [x])
        europa_sell_record['卖出金额最后一个'] = europa_sell_record['卖出金额列表'].apply(lambda x: str(int(float(x[-1]) // 1e4)))
        message += f'当日卖出总金额：{europa_sell_record["卖出金额最后一个"].astype(int).sum()}\n'
        europa_sell_record['message'] = europa_sell_record['证券名称'] + '(' + europa_sell_record["卖出金额最后一个"] + ')'
        message += f'买入：{"，".join(europa_buy_record["message"].tolist())}\n'
        message += f'卖出：{"，".join(europa_sell_record["message"].tolist())}'
        # message += '-' * 10 + '\n'
    except:
        message += '***europa当日没有数据'

    """
    #%% saturn策略跟踪
    saturn_fpath = root_path + 'saturn成交记录-%s.xlsx' % today_date
    saturn_record = pd.read_excel(saturn_fpath, sheet_name='累计卖出明细')
    saturn_record = saturn_record.query(f'买入日期 >= "{today_date_str}" & 成交金额 > 0')
    
    #%% ceres策略跟踪
    ceres_fpath = root_path + 'ceres成交记录-%s.xlsx' % today_date
    ceres_record = pd.read_excel(ceres_fpath, sheet_name='累计卖出明细')
    """
    send_message(message)

daily_strat_tracking(today_date=today_date, today_date_str=today_date_str)

# from dataApi import tradeDate
# date_list = tradeDate.get_date_range(20230206, 20230210)
# for dat in date_list:
#     print(dat)
#     today_date_str = pd.to_datetime(str(dat)).strftime('%Y-%m-%d')
#     daily_strat_tracking(today_date=dat, today_date_str=today_date_str)