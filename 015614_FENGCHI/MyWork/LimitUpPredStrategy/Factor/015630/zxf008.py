import sys
sys.path.append('/data/group/800442/800319')
from dataApi.tradeDate import *
from dataApi.getData import *
from LimitUpPredStrategy.Factor.tick_data_load import td,trans_daily_to_tick
import pandas as pd
import numpy as np
# 添加依赖因子
dependencies_factors = ['LastPx','LimitPool','TotalVolumeTrade']
# 导入因子
LimitPool = td.get_tick_factor('LimitPool')
stock_pool_stack = LimitPool[LimitPool].stack()
sup_df = pd.DataFrame(np.ones([LimitPool.shape[0],LimitPool.shape[1]]),index=LimitPool.index,columns=LimitPool.columns)

LastPx = td.get_tick_factor('LastPx')

open_day = get_daily_1factor('open',date_list=get_date_range(20130101,20210228),code_list=None,type='stock',diy_address=None)
open_tick = trans_daily_to_tick(open_day.shift(-1),sup_df)
open_tick = open_tick[LimitPool].stack()
open_tick = open_tick.reindex(stock_pool_stack.index)


LastPx = LastPx[LimitPool].stack()
LastPx = LastPx.reindex(stock_pool_stack.index)
pct = LastPx/open_tick-1
threshold = 0.07
factor = pct*(pct>threshold)
#factor = factor[LimitPool].stack()
factor = factor.reindex(stock_pool_stack.index)
factor.to_pickle('/data/group/800442/800319/ZTfactors/Untested/zxf008.pkl')