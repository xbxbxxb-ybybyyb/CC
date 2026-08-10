import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_cfg4(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg4, self).__init__(required_columns=['close_zz500', 'open_zz500', 'weight_zz500', 'high_zz500', 'low_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # b/a衡量了这一分钟的股价波动
        a = data['high_zz500'] - data['low_zz500']
        a[a<1e-5] = np.nan
        b = (data['close_zz500']-data['open_zz500'])
        b[b<0] = np.nan
        c = ts_sum(b/a, 60)
        factor = (c * data['weight_zz500']).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 200*6)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
