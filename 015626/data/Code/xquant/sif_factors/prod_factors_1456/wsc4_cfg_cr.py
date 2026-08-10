import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc4_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc4_cfg_cr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_index_corr_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # dpo技术指标，比较当前close与前一段时间的close均线
        stk_close = data['close_zz500']
        N = 20
        dpo = stk_close - ts_delay(ts_mean(stk_close, N), int(N/2+1))
        factor_init = dpo
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = 0
        # factor[factor>=0.5] = np.nan
        return factor
