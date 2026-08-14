# @Time : 2022/4/18 9:03
# @Author : Zhichen Lu
# @File : data_cleaning.py

import pandas as pd
import numpy as np
from xquant.thirdpartydata.marketdata import MarketData

md = MarketData()
#Tick数据
tick_open = md.getMDSecurityTickDataFrame('000001.SZ','20170313090000','20170313093000',0)
tick_close = md.getMDSecurityTickDataFrame('000001.SZ','20170313145700','20170313150000',0)
# 逐笔成交
trans_open = md.getMDTransactionDataFrame ('000001.SZ','20170313090000','20170313093000')
trans_close = md.getMDTransactionDataFrame ('000001.SZ','20170313145700','20170313150000')
# 逐笔委托
order_open = md.getMDOrderDataFrame('000001.SZ','20170313090000','20170313093000')
order_close = md.getMDOrderDataFrame  ('000001.SZ','20170313145700','20170313150000')

"""
table_type	string	数据表名称(
Stock-股票，
Index-指数，
Transaction-逐笔成交，
Order-逐笔委托，Kline1M4ZT-分钟K线，EnhancedKline1M-增强K线)
security_id	string	证券ID
date	string	年月日，格式为’YYYYmmdd’
trading_phase_code	list	取哪些市场阶段状态，默认取所有。所需的交易阶段代码
(
‘0’表示开盘前，启动。
‘1’表示开盘集合竞价。
‘2’表示开盘集合竞价阶段结束到连续竞价阶段开始之前。
‘3’表示连续竞价。
‘4’表示中午休市。
‘5’表示收盘集合竞价。
‘6’表示已闭市。
‘7’表示盘后交易（实际未使用）。)。
注意：TRANSACTION和ORDER和KLINE1M4ZT无此参数
sort_by_receive_time	bool	默认为False，按数据到达时间排序，True-按ReceiveDateTime排序，False-按MDTime排序。
"""
from xquant.marketdata import MarketData
mdp = MarketData()
close_stock = mdp.get_data_by_date("Stock", "000001.SZ", "20180301", ["5"], sort_by_receive_time=True)
close_order = mdp.get_data_by_date("Order", "000001.SZ", "20180301", ["5"], sort_by_receive_time=True)
close_trans = mdp.get_data_by_date("Transaction", "000001.SZ", "20180301", ["5"], sort_by_receive_time=True)

close_trans = close_trans[close_trans['MDTime']>='145700000']
close_order = close_order[close_order['MDTime']>='145700000']

open_stock = mdp.get_data_by_date("Stock", "000001.SZ", "20180301", ["1"], sort_by_receive_time=True)
open_order = mdp.get_data_by_date("Order", "000001.SZ", "20180301", ["1"], sort_by_receive_time=True)
open_trans = mdp.get_data_by_date("Transaction", "000001.SZ", "20180301", ["1"], sort_by_receive_time=True)


