from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts34_future_nr_vs(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'high' + suffix,'low' + suffix,'volume' + suffix,'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts34_future_nr_vs, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        factor = ((df['close' + suffix]-df['low' + suffix])-(df['high' + suffix]-df['close' + suffix]))/(df['high' + suffix]-df['low' + suffix])*df['volume' + suffix]
        factor = ts_mean(factor, 150)

        factor = rolling_normalize(factor, 5 * 242)

        factor = factor * df['stk_volatility' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = rolling_normalize(factor, 5 * 242)
        factor.columns = [columnname]

        return factor