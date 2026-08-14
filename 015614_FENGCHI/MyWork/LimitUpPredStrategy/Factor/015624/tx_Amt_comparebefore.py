import numpy as np
import pandas as pd
from tqdm import tqdm
import bottleneck as bk
import time
from backtest.factor_backtest.TickDataPrepare import TickDataPrepare
sys.path.append('/data/group/800442/800319')
from dataApi import getData, tradeDate, stockList
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int,trans_datetime2int,trans_int2windcode
from LimitUpPredStrategy.Factor.tick_data_load import TickData

td = TickData(start_date=20140101, end_date=20210228, start_tick=91500, end_tick=150000, return_idx=True)
# 添加依赖因子
dependencies_factors = ['LimitPool','TotalValueTrade']
# 导入因子
for item in dependencies_factors:
    exec('%s = td.get_tick_factor(\'%s\')' % (item, item))

stock_pool_stack = LimitPool[LimitPool].stack()
save_path='/data/group/800442/800319/ZTfactors/Untested/'
factor_name = 'Amt_comparebefore'

all_Value = TotalValueTrade[LimitPool].stack() / 1000
amt = getData.get_daily_1factor('amt', date_list=LimitPool.index.levels[0].to_list(),
                                code_list=LimitPool.index.levels[1].to_list()).shift(1)
amt = amt.rolling(5).mean()
amt = amt.stack().loc[LimitPool.index]
amt = amt.loc[stock_pool_stack.index]

all_Value = all_Value.loc[stock_pool_stack.index]

factor = all_Value / amt
factor.replace(np.inf, 0, inplace=True)
factor = factor.loc[stock_pool_stack.index]
factor.to_pickle(save_path+'tx_' + factor_name + '.pkl')

