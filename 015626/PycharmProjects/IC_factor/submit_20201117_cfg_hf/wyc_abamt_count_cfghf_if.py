from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_abamt_count_cfghf_if(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['Ask1AmtMean_300','Bid1AmtMean_300']
        lookback_bars=2000
        super(wyc_abamt_count_cfghf_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        ask1_more_num = (df['Ask1AmtMean_300'] > df['Bid1AmtMean_300']).rolling(10).sum() - 5
        up = (ask1_more_num > 0).sum(axis=1)
        down = (ask1_more_num < 0).sum(axis=1)
        factor = up / (up + down)
        factor = factor.ewm(20, adjust=False).mean().to_frame()
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor[factor < 0] = 0

        factor.columns = [columnname]

        return factor