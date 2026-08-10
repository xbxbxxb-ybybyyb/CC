from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_nr_ts_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_nr_ts_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_hs300'
        stk_close = df['close' + suffix]
        stk_close[abs(stk_close) < 1e-8] = np.nan
        ifreturn = df['close' + suffix] / stk_close.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 100)
        factor = ts_mean(factor, 20)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]


        return factor