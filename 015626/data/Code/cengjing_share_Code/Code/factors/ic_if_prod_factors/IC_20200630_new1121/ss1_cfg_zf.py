from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal

def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

class ss1_cfg_zf(FactorGeneratorComplex):
    def __init__(self):
        required_columns = ['close_zz500','high_zz500','weight_boolean_zz500','amount_zz500']
        super(ss1_cfg_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_zz500']/data['close_zz500'].shift(1)-1
        vol = rtn.rolling(60,min_periods=30).std()
        ret = data['close_zz500']/(data['high_zz500'].shift(1).rolling(60,min_periods=30).max())-1
        facorg = ret/vol
        facorg = rolling_norm(facorg,242*5)
        ar = (data['amount_zz500'][data['weight_boolean_zz500']].rank(axis=1,pct=True))*2-1
        fac = (facorg*ar).sum(axis=1).rolling(5,min_periods=2).mean()
        sig = ts_rank(fac,242*5)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)