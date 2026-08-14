# coding: utf-8
# Author：fengchi863
# Date ：2025/5/22 10:06
import sys
sys.path.append('/data/user/015614/Lucien')

from xquant.tradedata import TradeData
trd = TradeData()
import pandas as pd
import datetime
from ProdWork.factor_model_compare.tools import gen_black_list
from MixedWork.GreyStockGenerator.tools import trans_any2code
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
from LucienUtil.StockUtil import StockUtil
lm = link.LinkMessage()
fd = FactorData()

today = datetime.datetime.now().strftime('%Y%m%d')
# today = '20250709'
today = fd.tradingday(today, -1)[0]
last_date = fd.tradingday(today, -2)[0]  # 昨日
llast_date = fd.tradingday(today, -3)[0]

# 获取昨日ST个股
risk_df0 = fd.get_factor_value('WIND_AShareST', mddate=[last_date])
risk_list0 = list(risk_df0[((risk_df0['REMOVE_DT'] >= last_date) | (risk_df0['REMOVE_DT'].isnull())) & (risk_df0['S_TYPE_ST'] != 'R')]['S_INFO_WINDCODE'])
print(f'{last_date}共有ST股票{len(risk_list0)}只')

# 获取今日ST个股
risk_df1 = fd.get_factor_value('WIND_AShareST', mddate=[today])
risk_list1 = list(risk_df1[risk_df0['REMOVE_DT'].isnull() & (risk_df1['S_TYPE_ST'] != 'R')]['S_INFO_WINDCODE'])
print(f'{today}共有ST股票{len(risk_list1)}只')

# 今日新增ST股
new_st = list(set(risk_list1).difference(set(risk_list0)))
# 今日减少ST股
old_st = list(set(risk_list0).difference(set(risk_list1)))

old_st = [f'{x}({StockUtil.get_1stock_name(x)})' for x in old_st]

yestoday_black_list, _, _ = gen_black_list(last_date)
pre_st_list = pd.read_excel(f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{llast_date}.xlsx').index.map(trans_any2code).tolist() # 历史原因，文件名为前日，但是表为昨日
has_in_black = list(set(new_st).intersection(set(yestoday_black_list)))
has_in_pre_st = list(set(new_st).intersection(set(pre_st_list)))
not_in_pre_st = list(set(new_st).difference(set(pre_st_list)))

msg = ''
msg += f'{last_date}共有ST股票{len(risk_list0)}只\n'
msg += f'{today}共有ST股票{len(risk_list1)}只\n'
msg += f'今日新增ST个股：{",".join(new_st)}\n'
msg += f'今日减少ST个股：{"，".join(old_st)}\n'
msg += f'新增黑名单个股已在黑名单：{",".join(has_in_black)}\n'
msg += f'新增黑名单个股已在pre_st：{",".join(has_in_pre_st)}\n'
msg += f'新增黑名单个股不在pre_st：{",".join(not_in_pre_st)}\n'
msg += '----------------------------\n'

#%% 成交记录中的ST股检测
trd_df = trd.get_transaction_data('EventDriven', today, today, 3)
msg += f'使用当日持仓{today}持仓记录\n'

if len(trd_df) == 0:
    trd_df = trd.get_transaction_data('EventDriven', last_date, last_date, 3)
    print(f'使用昨日{last_date}持仓记录')

trd_df = trd_df.query('holdingqty > 0')
list(trd_df['assetaccount'].unique())
# 获取被ST个股
risk_df = fd.get_factor_value('WIND_AShareST')
risk_list = list(risk_df[risk_df['REMOVE_DT'].isnull() & (risk_df['S_TYPE_ST'] != 'R')]['S_INFO_WINDCODE'])

holding_st_list = list(set(trd_df['securityid'].map(trans_any2code).tolist()).intersection(risk_list))
print(list(set(trd_df['securityid'].tolist()).intersection(risk_list)))
msg += '当前持有ST股票：' + ','.join(holding_st_list)

lm.sendMessage(msg)
print(msg)

# str1 = '1305,1403,1404,1304,2000000206,2000000205,2000000107,2000000106,1835,1834,1833,1832,1831,1710,1709,1708,1707,1706,1733,1732,1731,1810,1805,1806,1807,1808,1809,1812,1712,1711,1811,2000000705,2000000605,1804,1803,1802,1801,1705,1704,1703,1702,1701,2000001400,2000001300,2000000103,2000000202,2000000100,2000000101,2000000200,2000000201,2000000102'
# str2 = '2000000705,2000000605,1406,1405,1404,1403,1402,1401,1400,2000001400,2000001300,1307,1306,1305,1304,1300,1733,1732,1731,1723,1722,1721,1720,1712,1711,1710,1709,1708,1707,1706,1705,1704,1703,1702,1701,1832,1831,1822,1821,1820,1812,1811,1810,1809,1808,1807,1806,1805,1804,1803,1802,1801,2000000100,2000000206,2000000205,2000000107,2000000106,2000000200,2000000201,2000000102,2000000101'
# set_xly = set(str1.split(','))
# set_me = set(str2.split(','))
# set_me.difference(set_xly)