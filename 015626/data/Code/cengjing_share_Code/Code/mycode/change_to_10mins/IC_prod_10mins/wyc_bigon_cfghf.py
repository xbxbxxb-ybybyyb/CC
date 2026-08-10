from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_bigon_cfghf(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['BuyUniqueOrderNum_500','BuyTradeNum_500']
        lookback_bars=2000
        super(wyc_bigon_cfghf, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        btn = df['BuyTradeNum_500'].copy()
        btn[abs(btn) < 1e-8] = np.nan
        factor = 1 - df['BuyUniqueOrderNum_500'] / btn

        factor = factor.sum(axis=1).to_frame()
        # factor = ts_mean(factor, 3)
        factor = ts_rank(factor, 3 * 237)
        factor.columns = [columnname]

        return factor