from LimitUpPredStrategy.Factor.tick_data_load import td
import pandas as pd
import numpy as np
# 添加依赖因子
dependencies_factors = ['LastPx','LimitPool']
# 导入因子
LimitPool = td.get_tick_factor('LimitPool')
stock_pool_stack = LimitPool[LimitPool].stack()
LastPx = td.get_tick_factor('LastPx')
factor = LastPx/LastPx.rolling(5,axis=1).min()
factor = factor[LimitPool].stack()
factor = factor.reindex(stock_pool_stack.index)
factor.to_pickle('/data/group/800442/800319/ZTfactors/Untested/zxf004.pkl')