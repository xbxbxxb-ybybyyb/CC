import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc18_cfg_as(FactorGeneratorComplex):
    def __init__(self):
        super(wsc18_cfg_as, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        bool_mask = data['weight_boolean_zz500']
        amount_mask = stk_amount[bool_mask]


        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        n = 20
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        r[abs(r)<1e-8] = np.nan
        m[abs(m)<1e-8] = np.nan
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open)) / r * k / m
        factor_init = si

        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 1200)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.7] = 0
        #factor[factor>=0.5] = np.nan
        return factor