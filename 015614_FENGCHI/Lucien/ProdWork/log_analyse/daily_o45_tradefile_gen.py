# coding: utf-8
# Author：fengchi863
# Date ：2024/12/13 14:31

import pandas as pd

"""

entrustdirection
securityname
securityid
tradedate
tradingaccount

lastamount
lastpx
lastqty

"""
import sys
import os
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
from xquant.tradedata import TradeData
trd = TradeData()

# nowdate = '20241220'
nowdate = dt.datetime.now().strftime('%Y%m%d')
strategy = trd.get_transaction_data("EventDriven", nowdate, nowdate, 2)
if nowdate == dt.datetime.now().strftime('%Y%m%d'):
    strategy.to_excel(f'/data/group/800463/日内强势股/实盘分析记录/Xquant接口下载成交回报/{nowdate}.xlsx')
# strategy = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/Xquant接口下载成交回报/20241218.xlsx')

# strategy = pd.concat([strategy1, strategy2, strategy3, strategy4, strategy5], axis=0)
strategy = strategy[['tradedate', 'securityid', 'securityname', 'entrustdirection', 'tradingaccount', 'lastamount', 'lastpx', 'lastqty']]
# group = strategy1.groupby(['tradedate', 'securityid', 'entrustdirection', 'tradingaccount']).agg({'lastamount': sum, 'lastqty': sum})
group = strategy.groupby(['tradedate', 'securityid', 'entrustdirection', 'tradingaccount']).agg({'lastamount': sum, 'lastqty': sum})
group = group.reset_index()
group['mean_price'] = group['lastamount'] / group['lastqty']
# set(group['tradingaccount'].tolist()) # 检查组合名称是否全部配上了，如果没有配齐，询问谢总或者徐老师，这里要求谢总每次添加了新的组合，通知我和徐老师
group = group.rename({'tradedate': '业务日期',
                      'securityid': '证券代码',
                      'securityname': '证券名称',
                      'tradingaccount': '组合名称',
                      'entrustdirection': '委托方向',
                      'lastamount': '成交金额',
                      'lastqty': '成交数量',
                      'mean_price': '成交均价'}, axis=1)
group['业务日期'] = group['业务日期'].map(str).apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:8])
group['证券代码'] = group['证券代码'].apply(lambda x: str(x).zfill(6))
group['委托方向'] = group['委托方向'].apply(lambda x: '买入' if x == 1 else '卖出')

group.to_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/O45_成交流水_%s_xquant.xls' % nowdate)

from dataApi.sendInfo import send_message
send_message(f'O45_成交流水_{nowdate}_xquant.xls 已保存')

"""
# 校验O45取出的文件
o45_deal = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_20241218_bak.xls')
set(o45_deal['组合名称'].tolist())
"""

# check.columns.tolist()
# print(check)
