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

close_day = get_daily_1factor('close',date_list=get_date_range(20130101,20210228),code_list=None,type='stock',diy_address=None)
close_tick = trans_daily_to_tick(close_day,sup_df)
close_tick = close_tick[LimitPool].stack()
close_tick = close_tick.reindex(stock_pool_stack.index)

pct2 = LastPx.pct_change(axis=1)
pct2 = pct2[LimitPool].stack()
pct2 = pct2.reindex(stock_pool_stack.index)
LastPx = LastPx[LimitPool].stack()
LastPx = LastPx.reindex(stock_pool_stack.index)
pct = LastPx/close_tick-1
threshold = 0.07
factor = pct2*(pct>threshold)
#factor = factor[LimitPool].stack()
factor = factor.reindex(stock_pool_stack.index)
factor.to_pickle('/data/group/800442/800319/ZTfactors/Untested/zxf009.pkl')