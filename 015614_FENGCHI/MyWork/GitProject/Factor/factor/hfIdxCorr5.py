import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def rolling_ewm(df, n):
    seq = [(1 - (2.0 / (n + 1))) ** (n - i) for i in range(1, n + 1)]
    weight = np.array(seq)
    return df.rolling(window=n).apply(lambda x: np.nansum(x * weight) / max(weight[np.isnan(x)].sum(), 1. / n))


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class hfIdxCorr5(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_adj_minute', 'FactorData.Basic_factor.free_float_shares',
                   'FactorData.Basic_factor.close']
    lag = 1
    reform_window = 5
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close_min = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']
        stk_code = close_min.columns.union(ffs.columns).union(close.columns)
        close_min = close_min.reindex(columns=stk_code).values
        ffs = ffs.reindex(columns=stk_code).values[0]
        close = close.reindex(columns=stk_code).values[0]
        ffc = ffs * close
        netv = close_min / close_min[0]
        index_netv = np.nansum(ffc * netv / np.nansum(ffc), axis=1)
        index_netv = index_netv.reshape(len(index_netv), 1).dot(np.ones((1, len(stk_code))))
        result = array_corr_np(index_netv, netv)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = rolling_ewm(temp_result, 5)
        return alpha
