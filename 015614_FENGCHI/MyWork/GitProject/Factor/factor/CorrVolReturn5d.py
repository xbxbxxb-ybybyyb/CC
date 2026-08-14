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


class CorrVolReturn5d(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_adj_minute', 'FactorData.Basic_factor.volume_adj_minute']
    lag = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        stk_code = close.columns
        close = close.values
        vol = vol.values
        p, v = np.nan * np.ones((6, len(stk_code))), np.nan * np.ones((6, len(stk_code)))
        for i in range(1, 6):
            p[i] = close[(i + 1) * 240 - 1] / close[i * 240 + 30] - 1
            v_0 = np.nansum(vol[(i - 1) * 240 + 30: i * 240], axis=0)
            v_1 = np.nansum(vol[i * 240 + 30: (i + 1) * 240], axis=0)
            v[i] = np.log(v_1 / v_0)
        p, v = pd.DataFrame(p[1:]).rank(axis=1).values, pd.DataFrame(v[1:]).rank(axis=1).values
        result = pd.Series(-array_corr_np(p, v), index=stk_code)
        return result
