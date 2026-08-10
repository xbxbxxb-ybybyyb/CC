from factor_generator import FactorGenerator
from operators_wyc import *


class wyc_if_2hour_return(FactorGenerator):
    def __init__(self):
        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_if_2hour_return, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']

        cif = df['close_if']
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = mean(ifreturn, 200)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor<0]=0
        return factor