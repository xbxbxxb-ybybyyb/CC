import sys
sys.path.append('/data/group/800442/800319')
from dataApi.tradeDate import *
from dataApi.getData import *
from LimitUpStrategy.TickDataPrepare2 import TickDataPrepare,open_ticks,trade_ticks,trade_items
from LimitUpPredStrategy.Factor.tick_data_load import td,trans_daily_to_tick
from LimitUpPredStrategy.Factor.FactorTest import FactorTest
import pandas as pd
import numpy as np

def abss(x):
    return np.abs(x)

def sqrt(x):
    return np.sqrt(np.abs(x)) * np.sign(x)

def square(x):
    return x ** 2

def cube(x):
    return x ** 3

def neg(x):
    return -x

def exp(x):
    return np.exp(x) - 1

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def max2(x, y):
    return np.fmax(x, y)

def _min2(x, y):
    return np.fmin(x, y)

def deviation2(x, y):
    return np.where(x + y != 0, (x - y) / (x + y), 0)

def mul2(x, y):
    return x * y

def sum2(x, y):
    return x + y

def sub2(x, y):
    return x - y

def abs_sub2(x, y):
    return abss(sub2(x, y))

def percent2(x, y):
    return (x - y) / abss(y)

def pn_condition2(x, y):
    return np.where(x > 0, y, -y)
dp = TickDataPrepare() # 实例化类
def read_basic_factor(name):
    return dp.get_data_by_date_list(item=name,  # Tick字段名, 支持的字段见tick_items列表，
                             # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                             start_date=20140101,
                             end_date=20210228,
                             date_list=None,  # 若传列表则忽略start_date和end_date参数
                             start_tick=91500,  # 默认为91500
                             end_tick=150000,  # 默认为150000
                             tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                             return_idx=True  # True返回DataFrame, False返回2darray
                             )
self = FactorTest(start_date=20140101,
                      backtest_start_date=20140701, end_date=20191231,
                      stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl')
LimitPool = read_basic_factor('LimitPool')
stock_pool_stack = LimitPool[LimitPool].stack()

expression = 'sum2(TotalBidQty, percent2(sub2(mul2(TotalBidQty, LowPx), TotalVolumeTrade), abs_sub2(sqrt(LastPx), neg(Buy2Price))))'
basic_factors = []
for i in trade_items:
    if i in expression:
        basic_factors.append(i)
for basic_factor in basic_factors:
    exec('%s = read_basic_factor(\'%s\')' % (basic_factor, basic_factor))
    exec('%s = %s[LimitPool].stack()' % (basic_factor, basic_factor))
    exec('%s = %s.reindex(stock_pool_stack.index)' % (basic_factor, basic_factor))
exec('factor = %s'%expression)
factor_name = 'zxf021'
exec('factor = pd.Series(factor,index=stock_pool_stack.index)')
path = '/data/group/800442/800319/ZTfactors/Untested/%s.pkl'%factor_name
exec('factor.to_pickle(\'%s\')'% path)
self.factor_test(factor_name,expression)