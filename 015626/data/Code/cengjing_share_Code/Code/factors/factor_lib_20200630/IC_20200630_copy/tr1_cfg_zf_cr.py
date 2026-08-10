from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class tr1_cfg_zf_cr(FactorGeneratorComplex):
    def __init__(self):
        required_columns = ['close_zz500','high_zz500','low_zz500','stk_index_corr_zz500']
        super(tr1_cfg_zf_cr, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        hh = data['high_zz500'].rolling(242,min_periods=30).max()
        ll = data['low_zz500'].rolling(242,min_periods=30).min()
        fac = 2*data['close_zz500']/(hh+ll)
        facorg = rolling_normalize(fac,242)
        cr = (data['stk_index_corr_zz500'].rank(axis=1,pct=True))*2-1
        fac = (facorg*cr).sum(axis=1).rolling(5,min_periods=5).mean()
        sig = pd.Series(bk.move_rank(fac.values,242*5,242),index=fac.index)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)