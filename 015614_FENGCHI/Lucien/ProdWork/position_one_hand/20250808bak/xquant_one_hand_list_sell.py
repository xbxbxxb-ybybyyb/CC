import os
import sys
sys.path.append('/data/user/015614/Lucien')

import datetime
import pandas as pd
from xquant.factordata import FactorData
from ProdWork.position_one_hand.get_stock_list import get_stock_list

"""
第二份代码是隔一段时间卖出因为channel变化，或者零股的股票，应该再剔除下st的股票，防止早上的时候徐馨怡已经卖掉了。
"""

s = FactorData()
from xquant.xqutils.helper import link

lm = link.LinkMessage()

assert os.system('pip install /data/user/019073/marketdata/installer_and_demo/xdb-2.0.0-cp36-cp36m-linux_x86_64.whl') == 0

from xdb.stockdata import StockData

a = StockData()

# 日期
today = datetime.datetime.now().strftime('%Y%m%d')
today = s.tradingday(today, -1)[0]
last_date = s.tradingday(today, -2)[0]  # 昨日

white_list, zz800_list, stock_list = get_stock_list(today)

hold_inf = pd.read_excel('/data/user/011477/EventDriven/eventshares_holding_%s.xlsx' % last_date)
not_use_list = pd.read_excel('/data/group/800463/xiely/sp/account/废弃股东_20240618.xlsx', dtype='str')['股东代码'].unique()
hold_inf = hold_inf[~hold_inf['股东代码'].isin(not_use_list)]
hold_inf = hold_inf[~hold_inf['证券代码'].str.startswith(('08', '38', '72', '75'))]  # 去除配债
hold_inf = hold_inf[~hold_inf['组合编号'].astype(str).str.startswith('200')]  # 去除主账户
hold_inf = hold_inf[(hold_inf['当前数量'] > 0)]

# 卖掉上海channel变更的股票
channel_dict = a.get_channel_info(last_date, "SH", [])
hold_sh = hold_inf[(hold_inf['证券代码'].str.endswith('SH'))]
hold_sh1 = hold_sh[hold_sh['组合编号'].isin([1702, 1703, 1704, 1705, 1701, 1732, 1733, 1720])].copy()
hold_sh2 = hold_sh[hold_sh['组合编号'].isin([1706, 1708, 1709, 1710, 1731, 1707, 1721, 1722])].copy()
print(hold_sh1['组合编号'].value_counts())
print(hold_sh2['组合编号'].value_counts())

# 第一份底仓
channel_no_dict1 = {1: [1720], 2: [1703], 3: [1705, 1733], 4: [1702], 5: [1704, 1732], 6: [1701]}
hold_sh1['组合编号_list'] = hold_sh1['证券代码'].apply(lambda stock: channel_no_dict1[channel_dict[stock]] if stock in channel_dict else [0])
hold_sh1['组合编号_list_str'] = hold_sh1['组合编号_list'].astype(str)
hold_sell_sh1 = hold_sh1[hold_sh1.apply(lambda x: x['组合编号'] not in x['组合编号_list'], axis=1)]
print(hold_sell_sh1.groupby(['组合编号'])['组合编号_list_str'].value_counts())

# 第二份底仓
channel_no_dict2 = {1: [1706], 2: [1709], 3: [1731, 1721], 4: [1708], 5: [1710, 1722], 6: [1707]}
hold_sh2['组合编号_list'] = hold_sh2['证券代码'].apply(lambda stock: channel_no_dict2[channel_dict[stock]] if stock in channel_dict else [0])
hold_sh2['组合编号_list_str'] = hold_sh2['组合编号_list'].astype(str)
hold_sell_sh2 = hold_sh2[hold_sh2.apply(lambda x: x['组合编号'] not in x['组合编号_list'], axis=1)]
# print(hold_sell_sh2.groupby(['组合编号'])['组合编号_list_str'].value_counts())

hold_sell = pd.concat([hold_sell_sh1, hold_sell_sh2])
sell_df = hold_sell.copy()
sell_df['买入交易账户'] = sell_df['组合编号'].astype(str)
sell_df['卖出交易账户'] = sell_df['组合编号'].astype(str)
sell_df['买入证券数量'] = 0
sell_df['卖出证券数量'] = sell_df['当前数量']
sell_df = sell_df[['证券代码', '买入交易账户', '卖出交易账户', '买入证券数量', '卖出证券数量']]
print(len(sell_df))
sell_df = sell_df.groupby('证券代码').head(1)
print(len(sell_df))
# sell_df=sell_df.groupby('卖出交易账户').head(89)
# print(len(sell_df))
SH_sell_df = sell_df[sell_df['证券代码'].str.endswith('SH')]
SZ_sell_df = sell_df[sell_df['证券代码'].str.endswith('SZ')]

print(SH_sell_df['卖出交易账户'].value_counts())
print(SZ_sell_df['卖出交易账户'].value_counts())

print('SH:', len(SH_sell_df))
print('SZ:', len(SZ_sell_df))

message = '孔老师，今天需要交易%s只（其中上海%s，深圳%s）' % (len(SH_sell_df) + len(SZ_sell_df), len(SH_sell_df), len(SZ_sell_df))
print(message)
lm.sendMessage(message)

path = '/data/user/011477/Trade_Docs/%s/Tuna/' % today
if not os.path.exists(path):
    os.makedirs(path)
SH_sell_df.to_excel('%s/%s_sell_list_SH.xlsx' % (path, today), index=False)
SZ_sell_df.to_excel('%s/%s_sell_list_SZ.xlsx' % (path, today), index=False)

# ——————卖出列表：低于1手——————
hold_inf = pd.read_excel('/data/user/011477/EventDriven/eventshares_holding_%s.xlsx' % last_date)
not_use_list = pd.read_excel('/data/group/800463/xiely/sp/account/废弃股东_20240618.xlsx', dtype='str')['股东代码'].unique()
hold_inf = hold_inf[~hold_inf['股东代码'].isin(not_use_list)]
hold_inf = hold_inf[~hold_inf['证券代码'].str.startswith(('08', '38', '72', '75'))]  # 去除配债
# 条件：非主账户，持仓>0，零股或科创板零股
condition = (~hold_inf['组合编号'].astype(str).str.startswith('200')) & (hold_inf['当前数量'] > 0) & (
            (hold_inf['当前数量'] < 100) | ((hold_inf['当前数量'] < 200) & (hold_inf['证券代码'].str.startswith('68'))) | (~hold_inf['证券代码'].isin(stock_list)))
hold_sell = hold_inf[condition]
hold_sell .to_excel('')

# 备注：这份代码是隔一段时间卖出因为channel变化，或者零股的股票，应该再剔除下st的股票。
