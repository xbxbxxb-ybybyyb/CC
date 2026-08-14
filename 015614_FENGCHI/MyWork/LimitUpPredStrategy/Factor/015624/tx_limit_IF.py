import numpy as np
import pandas as pd
from tqdm import tqdm
import bottleneck as bk
import time
from ConceptApi import *
from backtest.factor_backtest.TickDataPrepare import TickDataPrepare
sys.path.append('/data/group/800442/800319')
from dataApi import getData, tradeDate, stockList
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int,trans_datetime2int,trans_int2windcode
from LimitUpPredStrategy.Factor.tick_data_load import TickData

td = TickData(start_date=20140101, end_date=20210228, start_tick=91500, end_tick=150000, return_idx=True)
# 添加依赖因子
dependencies_factors = ['LimitPool','LastPx', 'Buy1Price']
# 导入因子
for item in dependencies_factors:
    exec('%s = td.get_tick_factor(\'%s\')' % (item, item))

stock_pool_stack = LimitPool[LimitPool].stack()
save_path='/data/group/800442/800319/ZTfactors/Untested/'

factor_name = 'limit_IF'

Limit_stock =  get_basic_values('Limit_stock', start_date=LimitPool.index.levels[0][0], end_date=LimitPool.index.levels[0][-1]).shift(1)
low = getData.get_daily_1factor('low', date_list=LimitPool.index.levels[0].to_list(),code_list=LimitPool.index.levels[1].to_list()).shift(1)
high = getData.get_daily_1factor('high', date_list=LimitPool.index.levels[0].to_list(),code_list=LimitPool.index.levels[1].to_list()).shift(1)

factor=Limit_stock*1+(low == high)*1
factor=factor.astype(float)
factor = factor.stack().loc[LimitPool.index]
factor = factor.loc[stock_pool_stack.index]

factor = factor.loc[stock_pool_stack.index]
factor.to_pickle(save_path+'tx_' + factor_name + '.pkl')
