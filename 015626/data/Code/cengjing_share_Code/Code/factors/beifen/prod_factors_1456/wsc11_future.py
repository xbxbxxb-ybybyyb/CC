import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from help_functions_wsc import *


class wsc11_future(FactorGenerator):
    def __init__(self):
        super(wsc11_future, self).__init__(required_columns=['close', 'high', 'low', 'open', 'recent_month_mask'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        mask = data['recent_month_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        open = data['open']
        n = 20
        a = abs(high-ts_delay(close, 1))
        b = abs(low-ts_delay(close, 1))
        c = abs(high-ts_delay(low, 1))
        d = abs(ts_delay(close, 1)-ts_delay(open, 1))
        k = np.maximum(a, b)
        m = ts_max(high-low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        si = 50 * (ts_delta(close, 1) + ts_delay(close, 1) - ts_delay(open, 1) + 0.5*(close - open)) / r * k / m

        #asi = si.cumsum()
        #M = 20
        #asima = ts_mean(asi, M)
        #factor = ts_delta(asima, 1)
        factor = si
        factor = ts_mean(factor, 90)
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        #factor[factor >= 0.5] = np.nan
        return factor
