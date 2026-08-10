import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import multi_processing_joblib
from operators_wsc import *


class wsc_cfg9(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg9, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'high_zz500', 'low_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # er技术指标。用来衡量市场的多空力量对比。
        # 在多头市场，人们会更贪婪地在接近高价的地方买入，BullPower越高则当前多头力量越强；而在空头市场，人们可能因为恐惧而在接近低价的地方卖出，BearPower越低则当前空头力量越强。
        # 当两者都大于0时，反映当前多头力量占据主导地位；两者都小于0则反映空头力量占据主导地位。
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_weight = data['weight_zz500']
        N = 30
        bull_power = stk_high - multi_processing_joblib(stk_close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        bear_power = stk_low - multi_processing_joblib(stk_close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        factor_init = bull_power + bear_power
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor = -ts_mean(factor_raw, 65)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 300*4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
