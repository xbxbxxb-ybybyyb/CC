# coding: utf-8
# Author：fengchi863
# Date ：2025/1/27 13:39

"""
检验成交记录中是否有将要退市的个股
"""

import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import pandas as pd
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator.tools import trans_any2code
from dataApi.sendInfo import send_message

fd = FactorData()
root_path = '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/'
today_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
today_date = 20250124

record_df = pd.read_excel(root_path + f'综合信息查询_成交回报_{today_date}.xls', sheet_name='Sheet1')
record_df = record_df.query('持仓 > 200')

stock_list = record_df['证券代码'].tolist()
stock_list = list(map(lambda x: trans_any2code(x), stock_list))


print(1)

