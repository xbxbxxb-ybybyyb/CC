# @Time : 2021/7/15 14:13
# @Author : Zhichen Lu
# @File : stock_pool_conponent.py
import pandas as pd
from dataApi.stockList import clean_stock_list

stock_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl').shift(1).rank(ascending=False, axis=1) < 600
param = dict(no_ST=False, least_live_days=1, no_pause=False, least_recover_days=0,
                     no_pause_limit=0, no_pause_stats_days=0, no_limit_up=False, no_limit_down=False,
                     other_limit=None, start_date=stock_pool.index[0], end_date=stock_pool.index[-1], trade_mode=False,)

pool_50 = clean_stock_list('SZ50',**param)
pool_300 = clean_stock_list('HS300',**param)
pool_500 = clean_stock_list('ZZ500',**param)
pool_1000 = clean_stock_list('ZZ1000',**param)
pool_1800 = clean_stock_list('COMMON',**param)

# union_stk_list = sorted(list(set(stock_pool.columns)|set(pool_50.columns)|set(pool_300.columns)|set(pool_500.columns)|set(pool_1000.columns)|set(pool_1800.columns)))

pool_component_stat = pd.DataFrame({
    '50成分股':(pool_50&stock_pool).sum(axis=1),
    '300成分股':(pool_300&stock_pool).sum(axis=1),
    '500成分股':(pool_500&stock_pool).sum(axis=1),
    '1000成分股':(pool_1000&stock_pool).sum(axis=1),
    '1800成分股':(pool_1800&stock_pool).sum(axis=1),
})

pool_component_stat['1800之后的股票'] = 600-pool_component_stat['1800成分股']
pool_component_stat['800之后的股票'] = 600 - pool_component_stat['300成分股'] - pool_component_stat['500成分股']
pool_component_stat = pool_component_stat[1:]

pool_component_pct = pool_component_stat/600