import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_ws(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_ws, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']

        # tii技术指标，首先计算dev=clos-close_ma，再分别对dev中正负部分各自ts_sum得到devpos和devneg(取负保证该值＞0)，最后计算devpos/(devpos+devneg)
        # 该值越大，表示过去一段上涨的越多，属于动量
        stk_close = data['close_zz500']
        n = 20
        m = int(n/2) + 1
        close_ma = ts_mean(stk_close, n)
        dev = stk_close - close_ma
        devpos = dev.copy(deep=True)
        devneg = -dev.copy(deep=True)
        devpos[devpos<0] = 0
        devneg[devneg<0] = 0
        sumpos = ts_sum(devpos, m)
        sumneg = ts_sum(devneg, m)
        temp = sumpos + sumneg
        temp[abs(temp)<1e-8] = np.nan
        tii = sumpos / temp
        factor_init = tii

        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 90)
        factor = rolling_norm(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
