from factor_generator import FactorGenerator
import pandas as pd
import numpy as np

def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class tr1_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['high_spot','low_spot','close_spot']
        super(tr1_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        hh = data['high_spot'].rolling(242,min_periods=30).max()
        ll = data['low_spot'].rolling(242,min_periods=30).min()
        sig = 2*data['close_spot']/(hh+ll)
        sig = rolling_normalize(sig,242)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)



        