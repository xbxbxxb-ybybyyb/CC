from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts7_future_nr_vr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'

        required_columns=['close' + suffix,'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts7_future_nr_vr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 15
        factor = (sma(sma(sma(log(df['close' + suffix]), N, 2), N, 2), N, 2) - delay(
            sma(sma(sma(log(df['close' + suffix]), N, 2), N, 2), N, 2), 1)) / delay(
            sma(sma(sma(log(df['close' + suffix]), N, 2), N, 2), N, 2), 1)
        factor = ts_mean(factor, 10)

        factor = rolling_normalize(factor, 5 * 242)

        vr = (2 * df['stk_volatility' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * vr
        factor = factor.sum(axis=1).to_frame()

        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor