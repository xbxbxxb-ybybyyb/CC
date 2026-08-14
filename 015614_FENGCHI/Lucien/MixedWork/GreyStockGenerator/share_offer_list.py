# coding: utf-8
# Author：fengchi863
# Date ：2022/9/27 14:59

"""
20220927：要约收购
像汇通能源，停牌发布要约收购公告，我们是可以在周一集合竞价参与的。你可以做个爬虫，只要有要约收购公告的股票都能及时关注到。

20221010：只对收购价大于10%以上的个股进行低频交易。针对不同的
"""

import sys
sys.path.append('/data/user/015614/Lucien')

from xquant.factordata import FactorData
from dataApi import tradeDate, stockList, sendInfo, getData
import pandas as pd
import datetime as dt

fd = FactorData()
today_date = int(dt.datetime.now().strftime('%Y%m%d'))
# next_trading_day = tradeDate.get_pre_trade_date(today_date, -1)
# next_trading_day_str = pd.to_datetime(str(next_trading_day)).strftime('%Y-%m-%d')

basic_info = fd.get_factor_value('WIND_AShareDescription')
basic_info = basic_info[['S_INFO_WINDCODE', 'S_INFO_NAME', 'S_INFO_COMPCODE']]
offer = fd.get_factor_value('WIND_AshareOfferforoffer')     # 此表实时更新
offer = pd.merge(offer, basic_info, how='inner', on='S_INFO_COMPCODE')
offer = offer.sort_values('OPDATE', ascending=False)
filter_col = ['S_INFO_WINDCODE',
              'S_INFO_NAME',
              'START_DATE',
              'END_DATE',
              'S_PROFITNOTICE_FIRSTANNDATE',
              'S_PROFITNOTICE_DATE',
              'S_RESULT_BULLETIN_DAY',
              'NANN_DATE',
              'OPDATE',  # 最后一次更新的时间
              'PURCHASING_PRICE'
              ]
offer = offer[filter_col]
offer = offer.reset_index(drop=True)

offer = offer.query(f'S_PROFITNOTICE_FIRSTANNDATE >= "{today_date}"')
if offer.shape[0] == 0:
    sendInfo.send_message('下一个交易日没有要约收购个股公告...')

rename_col = {
              'S_INFO_WINDCODE': '证券代码',
              'S_INFO_NAME': '证券名称',
              'START_DATE': '开始日期',
              'END_DATE': '结束日期',
              'S_PROFITNOTICE_FIRSTANNDATE': '首次公告日',
              'S_PROFITNOTICE_DATE': '要约收购书公告日',
              'S_RESULT_BULLETIN_DAY': '要约收购结果公告日',
              'NANN_DATE': '最新公告日期',
              'OPDATE': '最新更新时间',
              'PURCHASING_PRICE': '流通股每股收购价格'
}

offer = offer.rename(columns=rename_col)
offer['首次公告日'] = offer['首次公告日'].map(int)
offer['证券ID'] = offer['证券代码'].map(stockList.trans_windcode2int)
offer['最近交易日'] = offer['首次公告日'].apply(lambda x: x if x in tradeDate.trade_dates else tradeDate.get_pre_trade_date(x, -1))
offer['流通股每股收购价格'] = offer['流通股每股收购价格'].map(float)
offer = offer[~offer['流通股每股收购价格'].isna()]
offer = offer.reset_index(drop=True)

close = getData.get_daily_1factor('close')
offer['前收价'] = offer[['证券ID', '最近交易日']].apply(lambda x: close.iloc[-1][x['证券ID']], axis=1)
offer['收购价相对于前收价涨幅'] = offer['流通股每股收购价格'] / offer['前收价'] - 1

def format_message(offer):
    msg = ''
    for idx in range(len(offer)):
        msg += f'{offer["证券名称"][idx]}({round(offer["收购价相对于前收价涨幅"][idx], 2)})，'
    msg = msg[:-1]
    return msg

message = format_message(offer)

sendInfo.send_message(f'下一个交易日有要约收购个股公告：{message}')
