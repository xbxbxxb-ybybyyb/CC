import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc8_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc8_cfg_ar, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'weight_boolean_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        weight_true = data['weight_boolean_zz500']
        amount_mask = data['amount_zz500'][weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # ddi技术指标，先以high+low作为合成价格，然后以它向上or向下作为flag，作用到一个刻画标的向上or向下波动的指标上（abs(ts_delta(high, 1))， abs(ts_delta(low, 1))），即high和low的路径
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        n = 30
        hl = stk_high + stk_low
        high_abs = abs(ts_delta(stk_high, 1))
        low_abs = abs(ts_delta(stk_low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = ts_sum(dmz, n) + ts_sum(dmf, n)
        a[abs(a)<1e-8] = np.nan
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / a
        factor_init = ddi

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
