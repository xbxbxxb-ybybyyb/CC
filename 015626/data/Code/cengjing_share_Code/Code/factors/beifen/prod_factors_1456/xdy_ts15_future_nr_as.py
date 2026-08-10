from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts15_future_nr_as(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts15_future_nr_as, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'

        high = df['high' + suffix]
        high = multi_processing_joblib(df=high, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/11)
        a = ts_rank(high, 80)
        factor = ts_mean(a, 50)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0

        return factor