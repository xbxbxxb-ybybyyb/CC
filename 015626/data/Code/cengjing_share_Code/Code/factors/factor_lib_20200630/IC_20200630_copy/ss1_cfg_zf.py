from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class ss1_cfg_zf(FactorGeneratorComplex):
    def __init__(self):
        required_columns = ['close_zz500','high_zz500','weight_boolean_zz500','amount_zz500']
        super(ss1_cfg_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_zz500']/data['close_zz500'].shift(1)-1
        vol = rtn.rolling(60,min_periods=30).std()
        ret = data['close_zz500']/(data['high_zz500'].shift(1).rolling(60,min_periods=30).max())-1
        facorg = ret/vol
        facorg = rolling_normalize(facorg,242*5)
        ar = (data['amount_zz500'][data['weight_boolean_zz500']].rank(axis=1,pct=True))*2-1
        fac = (facorg*ar).sum(axis=1).rolling(5,min_periods=2).mean()
        sig = pd.Series(bk.move_rank(fac.values,242*5,242),index=fac.index)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)