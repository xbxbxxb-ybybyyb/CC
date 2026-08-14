# coding: utf-8
# Author：fengchi863
# Date ：2025/7/16 14:18

import os
import sys
sys.path.append('/data/user/015614/Lucien')

from LucienUtil import IO
import pandas as pd
import datetime
from xquant.factordata import FactorData
from ProdWork.position_one_hand.get_stock_list import get_stock_list
from ProdWork.position_one_hand.channel_config import *

s = FactorData()
from xquant.xqutils.helper import link

lm = link.LinkMessage()

assert os.system('pip install /data/user/019073/marketdata/installer_and_demo/xdb-2.0.0-cp36-cp36m-linux_x86_64.whl') == 0

from xdb.stockdata import StockData

"""
第一份代码主要包括以下内容，每天930定时任务，生成excel给孔剑阳：
（1）生成股票列表：白名单中已上市的股票，减去手动调整黑名单、pre_st黑名单、一字跌停黑名单、延迟回复黑名单、限售解禁黑名单等，减去前收盘价较低的股票，减去stpt的股票。
（2）买入列表：买入股票列表中持仓不足的部分。第一批账户买入europa和leda的底仓，上海按照channel分配到8个账户，深圳按照已持仓数量分配到7个账户；第二批账户买入jupiter的底仓，上海按照channel分配到8个账户，深圳按照已持仓数量分配到8个账户。
（3）卖出列表：卖出持仓中不符合要求的部分。包括小账户中不在股票列表的股票、主账户中因为隔离池没卖完的一手股票。
（4）生成tuna参数：不交易stpt的股票（tuna不交易，由徐馨怡人工卖出），不交易当天低频策略涉及的股票，分为两次启动（tuna每次启动一只股票只能一个账户）。
"""

a = StockData()

# 日期
today = datetime.datetime.now().strftime('%Y%m%d')
# today = '20250819'
today = s.tradingday(today, -1)[0]
last_date = s.tradingday(today, -2)[0]  # 昨日

white_list, zz800_list, stock_list = get_stock_list(today)

# 读取持仓列表
hold = pd.read_excel('/data/user/011477/EventDriven/eventshares_holding_%s.xlsx' % last_date)
not_use_list = pd.read_excel('/data/group/800463/xiely/sp/account/废弃股东_20240618.xlsx', dtype='str')['股东代码'].unique()
hold = hold[~hold['股东代码'].isin(not_use_list)]
hold = hold[~hold['证券代码'].str.startswith(('08', '38', '72', '75'))]  # 去除配债
hold = hold[~hold['组合编号'].astype(str).str.startswith('200')]  # 去除主账户
hold = hold[hold['当前数量'] >= 100]
hold_list = list(hold['证券代码'].unique())
hold_no = hold.groupby('组合编号').size()  # 17是上海,18是深圳
hold_no_new = hold_no.copy()
# for ind in [1720,1721,1722]:#新加的账户需要初始化
#     if ind not in hold_no_new.index:
#         hold_no_new.loc[ind]=0

# 读取上海的channel列表
channel_dict = a.get_channel_info(last_date, "SH", [])

# 生成需要购买的股票列表
SH_buy_list = [stock for stock in stock_list if stock[0] == '6']
SZ_buy_list = [stock for stock in stock_list if stock[0] != '6']

# 第二份底仓
# 读取上海的channel列表
channel_dict = a.get_channel_info(last_date, "SH", [])
channel_no_dict = sh_channel_no_dict2
SH_df1 = pd.DataFrame()
SH_df1['证券代码'] = SH_buy_list
for i in SH_df1.index:
    stock = SH_df1.loc[i, '证券代码']

    if stock == '688265.SH':
        print(1)

    if stock[:2] == '68':
        target_num = 200
    elif stock in zz800_list:
        target_num = 100
    else:
        target_num = 100

    need_buy = 0
    no = 0
    new_append = 0
    if stock not in channel_dict:
        print(stock, ':not in channel_dict')
    else:
        no_list = channel_no_dict[channel_dict[stock]]
        now_buy = hold[(hold['证券代码'] == stock) & (hold['组合编号'].isin(no_list))]['当前数量'].sum()
        if stock[:2] == '68':
            now_buy = int(now_buy / 200) * 200
        else:
            now_buy = int(now_buy / 100) * 100
        if now_buy < target_num:
            need_buy = target_num - now_buy
            if len(hold[(hold['证券代码'] == stock) & (hold['组合编号'].isin(no_list))]) == 0:  # 如果任何账户都没这个票的
                no = hold_no_new.loc[no_list].idxmin()  # 放到账户持有小单最小的小账户里
                new_append = 1
            else:  # 存在账户有这票的，就找到是在哪个账户里买的这个票
                no = hold[(hold['证券代码'] == stock) & (hold['组合编号'].isin(no_list))]['组合编号'].iloc[0]

    SH_df1.loc[i, '买入交易账户'] = str(no)
    SH_df1.loc[i, '卖出交易账户'] = str(no)
    SH_df1.loc[i, '买入证券数量'] = need_buy
    SH_df1.loc[i, '卖出证券数量'] = 0
    if new_append > 0:
        hold_no_new.loc[no] = hold_no_new.loc[no] + 1
SH_df1 = SH_df1[SH_df1['买入证券数量'] > 0]
SZ_df1 = pd.DataFrame()
SZ_df1['证券代码'] = SZ_buy_list
for i in SZ_df1.index:
    stock = SZ_df1.loc[i, '证券代码']

    if stock == '002622.SZ':
        print(1)

    need_buy = 0
    no = 0
    new_append = 0
    no_list = sz_channel_no_list2

    if stock in zz800_list:
        target_num = 100
    else:
        target_num = 100

    now_buy = hold[(hold['证券代码'] == stock) & (hold['组合编号'].isin(no_list))]['当前数量'].sum()
    now_buy = int(now_buy / 100) * 100
    if now_buy < target_num:
        need_buy = target_num - now_buy
        if len(hold[(hold['证券代码'] == stock) & (hold['组合编号'].isin(no_list))]) == 0:
            no = hold_no_new.loc[no_list].idxmin()
            new_append = 1
        else:
            no = hold[(hold['证券代码'] == stock) & (hold['组合编号'].isin(no_list))]['组合编号'].iloc[0]

    SZ_df1.loc[i, '买入交易账户'] = str(no)
    SZ_df1.loc[i, '卖出交易账户'] = str(no)
    SZ_df1.loc[i, '买入证券数量'] = need_buy
    SZ_df1.loc[i, '卖出证券数量'] = 0
    if new_append > 0:
        hold_no_new.loc[no] = hold_no_new.loc[no] + 1
SZ_df1 = SZ_df1[SZ_df1['买入证券数量'] > 0]

SH_df = pd.concat([SH_df1], sort=False)
SZ_df = pd.concat([SZ_df1], sort=False)
# print('需要买入的股票数量:SH%s（第一份%s，第二份%s）；SZ%s（第一份%s，第二份%s）' % (len(SH_df), len(SH_df1), len(SZ_df), len(SZ_df1)))


SH_all_df = pd.concat([SH_df], sort=False)
SZ_all_df = pd.concat([SZ_df], sort=False)
all_stpt_df = s.get_factor_value('Basic_factor', stock=list(SH_all_df['证券代码'].unique()) + list(SZ_all_df['证券代码'].unique()), mddate=[today], factor_names=['stpt'])
all_stpt_list = all_stpt_df[all_stpt_df['stpt'] == '1'].reset_index()['stock'].to_list()
SH_all_df = SH_all_df[~SH_all_df['证券代码'].isin(all_stpt_list)]  # 不交易ST股票，需要卖出ST股票由徐老师人工卖出
SZ_all_df = SZ_all_df[~SZ_all_df['证券代码'].isin(all_stpt_list)]  # 不交易ST股票，需要卖出ST股票由徐老师人工卖出

if os.path.exists(r'/data/group/800463/wangj/for_xly/低频测试/%s_上海席位_决策排序_rmul.xlsx' % today):
    sh_excel_df = pd.read_excel(r'/data/group/800463/wangj/for_xly/低频测试/%s_上海席位_决策排序_rmul.xlsx' % today, dtype=str)
    sh_excel_list = list(sh_excel_df['证券代码'].unique())
    print('低频策略SH：', sh_excel_list)
    SH_all_df = SH_all_df[~SH_all_df['证券代码'].isin(sh_excel_list)]
if os.path.exists(r'/data/group/800463/wangj/for_xly/低频测试/%s_深圳席位_决策排序_rmul.xlsx' % today):
    sz_excel_df = pd.read_excel(r'/data/group/800463/wangj/for_xly/低频测试/%s_深圳席位_决策排序_rmul.xlsx' % today, dtype=str)
    sz_excel_list = list(sz_excel_df['证券代码'].unique())
    print('低频策略SZ：', sz_excel_list)
    SZ_all_df = SZ_all_df[~SZ_all_df['证券代码'].isin(sz_excel_list)]

# 检查是否有相同股票、相同账户的
assert SH_all_df.groupby(['证券代码', '买入交易账户']).size().max() == 1
assert SZ_all_df.groupby(['证券代码', '买入交易账户']).size().max() == 1

SH_all_df1 = SH_all_df[~SH_all_df['证券代码'].duplicated()]
SH_all_df2 = SH_all_df[SH_all_df['证券代码'].duplicated()]
# SH_all_df.shape
# SH_all_df1.shape
# SH_all_df2.shape
# SH_all_df2 = SH_all_df2.sort_values('证券代码')
# SZ_all_df['duplicates'] = SZ_all_df['证券代码'].duplicated()
# SZ_all_df = SZ_all_df.sort_values('证券代码')
SZ_all_df1 = SZ_all_df[~SZ_all_df['证券代码'].duplicated()]
SZ_all_df2 = SZ_all_df[SZ_all_df['证券代码'].duplicated()]
SH_all_df2 = SH_all_df2.groupby('证券代码').head(1).sort_values('证券代码')  # 不支持重复标的
SZ_all_df2 = SZ_all_df2.groupby('证券代码').head(1).sort_values('证券代码')  # 不支持重复标的
print('SH:%s（第一批%s,第二批%s）' % (len(SH_all_df), len(SH_all_df1), len(SH_all_df2)))
print('SZ:%s（第一批%s,第二批%s）' % (len(SZ_all_df), len(SZ_all_df1), len(SZ_all_df2)))
SZ_all_df['duplicates'] = SZ_all_df['证券代码'].duplicated()
message = '孔老师，今天warehouse2需要交易%s只（其中上海%s，深圳%s），第二批需要交易%s只（其中上海%s，深圳%s）' \
          % (len(SH_all_df1) + len(SZ_all_df1), len(SH_all_df1), len(SZ_all_df1), len(SH_all_df2) + len(SZ_all_df2), len(SH_all_df2), len(SZ_all_df2))
print(message)
lm.sendMessage(message)
lm.sendMessage('!!!!!!!!!!!!!!!!!!!!!!!!')

path = '/data/user/011477/Trade_Docs/%s/Tuna/' % today
if not os.path.exists(path):
    os.makedirs(path)

SH_all_df1.to_excel('%s/%s_one_hand_warehouse2_SH1.xlsx' % (path, today), index=False)
SZ_all_df1.to_excel('%s/%s_one_hand_warehouse2_SZ1.xlsx' % (path, today), index=False)
SH_all_df2.to_excel('%s/%s_one_hand_warehouse2_SH2.xlsx' % (path, today), index=False)
SZ_all_df2.to_excel('%s/%s_one_hand_warehouse2_SZ2.xlsx' % (path, today), index=False)

# 发送消息给孔剑阳
from dataApi.sendInfo import send_message
send_message(message, ['015617', '022335'])