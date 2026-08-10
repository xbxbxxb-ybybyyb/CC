from overnight.factor_generator import FactorGenerator
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

def ts_mean(df1, d):
    # moving time-series average for the past d periods
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

def ts_rank(df1, d):
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

def rolling_norm(self, sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if isinstance(sig, pd.DataFrame):
            colnames = sig.columns
        elif isinstance(sig, pd.Series):
            colnames = sig.name
        sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                            index=sig.index, name=colnames)
        sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                            index=sig.index, name=colnames)
        temp = sig_max - sig_min
        temp[abs(temp) < 1e-8] = np.nan
        signal = (sig - sig_min) / temp
        return 2 * signal - 1

class wyc_if_2hour_return_nr_as_cfg(FactorGenerator):

    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix]
        super(wyc_if_2hour_return_nr_as_cfg, self).__init__(required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=3)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        cif = df['close' + suffix].between_time(datetime.time(9, 30), datetime.time(14, 57))
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        # factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix].between_time(datetime.time(9, 30), datetime.time(14, 57))
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 40)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor = factor.loc[factor.index.time == datetime.time(14,49)]
        factor = factor.resample('D').first()

        return factor