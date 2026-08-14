# @Time : 2021/7/29 21:23
# @Author : Zhichen Lu
# @File : OnlineDataVlidation.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
import pandas as pd
from online_conf import holding_info_path,buy_time_info_path,path_for_930
from dataApi.getData import trans_int2windcode
from dataApi.tradeDate import get_recent_trade_date,get_pre_trade_date
import datetime
from dataApi.sendInfo import send_message
import os

def format_df(df,port_id='201001',index=None):
    df['组合编号'] = df['组合编号'].apply(lambda x : str(x)[:len(port_id)])
    df = df[df['组合编号'].eq(port_id)].set_index('证券代码')
    if '交易市场' in df.columns:
        df = df[df['交易市场'].isin(['深交所A','上交所A'])]
    df.index = df.index.astype(int).map(trans_int2windcode)
    return df
today = 20211231#int(datetime.date.today().strftime('%Y%m%d'))
date =get_recent_trade_date(today)
holding = pd.Series(pd.read_pickle(f'{holding_info_path}{date}.pkl')).drop('cash')
holding_930 = pd.Series(pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')).drop('cash')

afternoon_port = pd.read_excel(f'/data/user/011477/order/O32/afternoon/综合信息查询_组合证券_{date}.xls')
afternoon_port = format_df(afternoon_port)
exist_holding = afternoon_port[afternoon_port['持仓']>0]['持仓']
union_stk = list(set(exist_holding.index).union(set(holding.index)).union(set(holding_930.index)))
param_holding = holding_930.reindex(union_stk).fillna(0) + holding.reindex(union_stk).fillna(0)

if (holding_930.reindex(union_stk).fillna(0) - exist_holding.reindex(union_stk).fillna(0)).max() != 0:
    send_message(['015664'],'930持仓多余O32')
    raise Exception('930持仓多余O32')

if (holding.reindex(union_stk).fillna(0) - exist_holding.reindex(union_stk).fillna(0)).max()!=0:
    send_message(['015664'], 'FIX持仓多余O32')
    raise Exception('FIX持仓多余O32')
if ((param_holding - exist_holding.reindex(union_stk).fillna(0)).max()!=0) or ((param_holding - exist_holding.reindex(union_stk).fillna(0)).min()!=0):
    send_message(['015664'], '总持仓不一致')
    raise Exception('总持仓不一致')

T0_list = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/share/stk_list{date}.pkl')
T0_path = list(map(lambda x : x.replace('.json',''),os.listdir(f'/data/user/666888/Makalu/parameters/EnsembleMonitor/EnsembleMonitor_{get_pre_trade_date(date,-1)}/')))

if set(T0_list) - set(T0_path):
    send_message(['015664'],f'股票池存在T0没有参数的股票{set(T0_list) - set(T0_path)}')

no_param_stk = list(filter(lambda x : x not in T0_path,union_stk))
if no_param_stk:
    send_message(['015664'],f'存在无T0参数持仓股票:{no_param_stk}')


send_message(['015664'],f'持仓股票正常')