from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_nr_as_cfg(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_nr_as_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        cif = df['close' + suffix]
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = ifreturn
        # factor = ts_mean(ifreturn, 200)

        # factor = ts_rank(factor, 2 * 237)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        # factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 3)
        factor = ts_rank(factor, 3 * 237)
        factor[factor >=0.5] = 0

        factor.columns = [columnname]


        return factor