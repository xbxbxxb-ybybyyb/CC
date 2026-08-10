import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_wsc import *


class wsc5_spot(FactorGenerator):
    def __init__(self):
        super(wsc5_spot, self).__init__(required_columns=['close_spot', 'high_spot', 'low_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # er技术指标。用来衡量市场的多空力量对比。
        # 在多头市场，人们会更贪婪地在接近高价的地方买入，BullPower越高则当前多头力量越强；而在空头市场，人们可能因为恐惧而在接近低价的地方卖出，BearPower越低则当前空头力量越强。
        # 当两者都大于0时，反映当前多头力量占据主导地位；两者都小于0则反映空头力量占据主导地位。
        close = data['close_spot']
        high = data['high_spot']
        low = data['low_spot']
        N = 30
        bull_power = high - ts_truncated_ema(close, d=60, alpha=(N-1)/(N+1))
        bear_power = low - ts_truncated_ema(index_close, d=60, alpha=(N-1)/(N+1))
        factor_raw = bull_power + bear_power
        factor_mean = -ts_mean(factor_raw, 180)
        factor = ts_rank(factor, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = np.nan
        return factor
