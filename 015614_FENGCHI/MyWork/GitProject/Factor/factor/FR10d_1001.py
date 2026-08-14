import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class FR10d_1001(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_adj_minute', 'FactorData.Basic_factor.amt',
                   'FactorData.Basic_factor.pre_close_badj']
    lag = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close_min = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        pre_close = database.depend_data['FactorData.Basic_factor.pre_close_badj']
        stk_code = close_min.columns.union(amt.columns).union(pre_close.columns)
        close_min, amt, pre_close = close_min.reindex(columns=stk_code), amt.reindex(
            columns=stk_code), pre_close.reindex(columns=stk_code)
        close_min, amt, pre_close = close_min.values, amt.values[-11:-1], pre_close.values[-10:]
        price = np.nan * np.ones((10, len(stk_code)))
        for i in range(1, 11):
            price[i-1] = close_min[240*i:240*(i+1)][30]
        ret = price / pre_close - 1
        result = array_corr_np(np.where(ret < 0, amt, np.nan), abs(ret))
        result = pd.Series(-result, index=stk_code)
        return result
