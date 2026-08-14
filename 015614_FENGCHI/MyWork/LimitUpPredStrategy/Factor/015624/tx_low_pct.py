import numpy as np
import pandas as pd
from tqdm import tqdm
import bottleneck as bk
from ConceptApi import *
import time
from backtest.factor_backtest.TickDataPrepare import TickDataPrepare
sys.path.append('/data/group/800442/800319')
from dataApi import getData, tradeDate, stockList
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int,trans_datetime2int,trans_int2windcode
from LimitUpPredStrategy.Factor.tick_data_load import TickData

td = TickData(start_date=20140101, end_date=20210228, start_tick=91500, end_tick=150000, return_idx=True)
# 添加依赖因子
dependencies_factors = ['LimitPool','LastPx', 'LowPx']
# 导入因子
for item in dependencies_factors:
    exec('%s = td.get_tick_factor(\'%s\')' % (item, item))

stock_pool_stack = LimitPool[LimitPool].stack()
save_path='/data/group/800442/800319/ZTfactors/Untested/'
factor_name = 'low_pct'

factor = LastPx / LowPx - 1
factor = factor[LimitPool].stack()
factor = factor.loc[stock_pool_stack.index]
factor.to_pickle(save_path+'tx_' + factor_name + '.pkl')

