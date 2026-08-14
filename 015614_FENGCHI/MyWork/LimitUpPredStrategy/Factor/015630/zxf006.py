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


close_day = get_daily_1factor('close_badj',date_list=get_date_range(20130101,20210228),code_list=None,type='stock',diy_address=None)
open_day = get_daily_1factor('open_badj',date_list=get_date_range(20130101,20210228),code_list=None,type='stock',diy_address=None)
pct = open_day/close_day.shift(1)
pct_to_tick = trans_daily_to_tick(pct,sup_df)
threshold = 0.07
pct_to_tick[pct_to_tick>0.09] = 1
pct_to_tick[(pct_to_tick>threshold)&(pct_to_tick<0.09)] = 2
pct_to_tick[pct_to_tick<threshold] = 3
factor = pct_to_tick[LimitPool].stack()
factor = factor.reindex(stock_pool_stack.index)
factor.to_pickle('/data/group/800442/800319/ZTfactors/Untested/zxf006.pkl')