# @Time : 2020/12/1 18:09
# @Author : Zhichen Lu
# @File : prepare_stock_pool.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from dataApi.stockList import clean_stock_list
from dataApi.getData import get_daily_1factor
from StrongStockModel.conf.path_config import root_path
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()
today = int(datetime.date.today().strftime('%Y%m%d'))
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
close_adj = get_daily_1factor('close_badj',date_list=stock_pool.index.tolist(),code_list=stock_pool.columns.tolist())
pre_close = close_adj.shift(1)*close/close_adj

flatten = (abs(open/close - 1)<1e-7)  & (abs(open/high - 1)<1e-7) & (abs(open/low - 1)<1e-7)
rise = (open/pre_close - 1)>0.04
down = (open/pre_close - 1)<-0.04

open_flatten = flatten & ((rise+down)>0)
# check = flatten & (down>0)
pd.to_pickle(open_flatten,'/data/group/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten.pkl')

for each in open_flatten:
    pd.to_pickle(~open_flatten[each],'/data/group/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten/%d.pkl'%each)
#    print(each)

final_pool = (~open_flatten & stock_pool)#.loc[20160104:]
pd.to_pickle(final_pool,root_path + 'stock_pool_without_limit_up_down.pkl')
pd.to_pickle(final_pool,root_path + 'stock_pool.pkl')
lm.sendMessage('股票池更新完成')