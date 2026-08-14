# @Time : 2021/4/1 18:18
# @Author : Zhichen Lu
# @File : stk_pool_update.py
import sys

sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')

import pandas as pd
from dataApi.stockList import clean_stock_list
from dataApi.getData import get_daily_1factor,trans_int2windcode
from StrongStockModel.conf.path_config import root_path
import datetime
from xquant.xqutils.helper import link
from online_conf import path_for_930
import os

lm = link.LinkMessage()
from dataApi.tradeDate import get_recent_trade_date
today = get_recent_trade_date()#int(datetime.date.today().strftime('%Y%m%d'))
print(today)

stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=20131220, end_date=int(today))
print(stock_pool.index[-1])
close = get_daily_1factor('close',date_list=stock_pool.index.tolist(),code_list=stock_pool.columns.tolist())
open = get_daily_1factor('open',date_list=stock_pool.index.tolist(),code_list=stock_pool.columns.tolist())
high = get_daily_1factor('high',date_list=stock_pool.index.tolist(),code_list=stock_pool.columns.tolist())
low = get_daily_1factor('low',date_list=stock_pool.index.tolist(),code_list=stock_pool.columns.tolist())
close_badj = get_daily_1factor('close_badj',date_list=stock_pool.index.tolist(),code_list=stock_pool.columns.tolist())
pre_close = close_badj.shift(1)*close/close_badj    # 前收的前复权收盘价

flatten = (abs(open/close - 1)<1e-7)  & (abs(open/high - 1)<1e-7) & (abs(open/low - 1)<1e-7)
rise = (open/pre_close - 1)>0.04
down = (open/pre_close - 1)<-0.04

open_flatten = flatten & ((rise+down)>0)
# check = flatten & (down>0)
pd.to_pickle(open_flatten,'/data/group/800442/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten.pkl')

for each in open_flatten:
   pd.to_pickle(~open_flatten[each],'/data/group/800442/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten/%d.pkl'%each)
#    print(each)

final_pool = (~open_flatten & stock_pool)#.loc[20160104:]
pd.to_pickle(final_pool,root_path + 'stock_pool_without_limit_up_down.pkl')
pd.to_pickle(final_pool,root_path + 'stock_pool.pkl')
lm.sendMessage('股票池更新完成%d'%stock_pool.index[-1])

###########
# exist_stk = get_daily_1factor('stock_list')
# stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl').loc[20210331]
stock_pool = stock_pool.loc[today]
stock_pool = stock_pool[stock_pool]
stock_pool.index = stock_pool.index.map(trans_int2windcode)
# restrict_pool = pd.read_pickle('/data/group/800319/strategy_local_path3/restrict_list.pkl')
# big_pool = list(filter(lambda x : (x not in restrict_pool) and (not x.startswith('688')),stock_pool.index.tolist()))
big_pool = stock_pool.index.tolist()

if os.path.exists(f'{path_for_930}{today}/StrategyOut/holding{today}.pkl'):
    holding_930 = pd.read_pickle(f'{path_for_930}{today}/StrategyOut/holding{today}.pkl')
    _ = holding_930.pop('cash')
else:
    holding_930 = []

from ExtraTools import get_nonfix_in_val
from dataApi.tradeDate import get_pre_trade_date

try:
    holding_info = get_nonfix_in_val('holding_info',get_pre_trade_date(today,-1),'/data/group/800319/strategy_local_path3/')
    holding = set(holding_info.keys()) - set(['cash'])
except:
    lm.sendMessage('生成交易池时，读取持仓失败！！！！！！')
    holding = []
big_pool = list(set(holding).union(set(big_pool)).union(holding_930))#.union(holding_930_sim))
lm.sendMessage(f'调仓可能使用的池子长度  {len(big_pool)}, 930:{len(holding_930)} FIX:{len(holding)}')
pd.to_pickle(big_pool,f'/data/user/015664/AFuckingTrigger/share/stk_list{today}.pkl')

