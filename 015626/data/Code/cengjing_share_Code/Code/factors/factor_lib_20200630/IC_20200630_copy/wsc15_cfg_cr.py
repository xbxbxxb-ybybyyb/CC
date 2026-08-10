import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc15_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc15_cfg_cr, self).__init__(required_columns=['close_zz500', 'stk_index_corr_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # vidya技术指标,vi可用来衡量股票过去一段时间的趋势，趋势越强vi值越大，此时vidya赋予当前的close更大的权重，捕捉趋势，反之同理。
        stk_close = data['close_zz500']
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 240)

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.3] = 0
        # factor[factor>=0.5] = np.nan
        return factor
