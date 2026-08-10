from factor_generator import FactorGenerator
import pandas as pd
import numpy as np


def rolling_normalize(sig, window=100):
    sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
    sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
    return ((sig - sig_min) / (sig_max - sig_min)) * 2 - 1


# tr1_zf
class fac_42(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close']

        super(fac_42, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, ccc):
        hh = data['high'].rolling(aaa, min_periods=1).max()
        ll = data['low'].rolling(aaa, min_periods=1).min()
        sig = 2 * data['close'] / (hh + ll)
        sig = ts_rank(sig, 300 * ccc)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
