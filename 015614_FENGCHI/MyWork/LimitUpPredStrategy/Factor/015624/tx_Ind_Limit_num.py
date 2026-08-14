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
dependencies_factors = ['LimitPool','LastPx']
# 导入因子
for item in dependencies_factors:
    exec('%s = td.get_tick_factor(\'%s\')' % (item, item))

stock_pool_stack = LimitPool[LimitPool].stack()
save_path='/data/group/800442/800319/ZTfactors/Untested/'

########因子92：T日涨停股票所在行业前4日的涨停股票数量#############
factor_name = 'Ind_Limit_num'

Limit_stock = get_basic_values('Limit_stock', start_date=td.start_date, end_date=td.end_date).shift(1)
CITICS1 = getData.get_daily_1factor('CITICS1', date_list=LimitPool.index.levels[0].to_list(),
                                    code_list=LimitPool.index.levels[1].to_list()).shift(1)
CITICS = CITICS1.apply(pd.value_counts)

ind_limit = pd.DataFrame(index=Limit_stock.index, columns=CITICS.index)
for ind in CITICS.index:
    ind_limit[ind] = Limit_stock[CITICS1 == ind].sum(axis=1)
ind_limit = ind_limit.rolling(4).sum()

stock_ind = pd.DataFrame(CITICS1.stack(), columns=['ind'])
stock_ind = stock_ind.reset_index()
ind_limit_num = pd.DataFrame(ind_limit.stack(), columns=['limit_num'])
ind_limit_num.index.names = ['date', 'ind']
ind_limit_num = ind_limit_num.reset_index()

a = pd.merge(stock_ind, ind_limit_num, left_on=['date', 'ind'], right_on=['date', 'ind'], how='inner')
factor = pd.pivot_table(a, index='date', columns='code', values='limit_num')

factor = factor.stack().loc[LimitPool.index]
factor = factor.loc[stock_pool_stack.index]
factor.to_pickle(save_path+'tx_' + factor_name + '.pkl')

