from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_abamt_count_cfg(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['Ask1AmtMean_500','Bid1AmtMean_500']
        lookback_bars=2000
        super(wyc_abamt_count_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        ask1_more_num = (df['Ask1AmtMean_500'] > df['Bid1AmtMean_500']).rolling(6).sum() - 3
        up = (ask1_more_num > 1).sum(axis=1)
        down = (ask1_more_num < -1).sum(axis=1)
        factor = up / (up + down)
        factor = factor.ewm(25, adjust=False).mean().to_frame()
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 6 * 242)
        factor[factor < -0] = 0
        factor.columns = [columnname]


        return factor