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


class MinCloseCallAmt5maCorrSharpe(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.close_minute',
                   'FactorData.Basic_factor.is_valid_raw']
    reform_window = 3

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        valid = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        stk_code = close.columns
        ret = close.pct_change(5).values[-180:]
        amt = amt.rolling(5, 1).mean().values[-180:]
        corr = array_corr_np(ret, amt)
        if len(corr[~np.isnan(corr)]) == 0:
            corr = np.zeros(len(corr))
        corr[np.isinf(corr)] = np.nan
        corr[corr == 0] = np.nan
        corr[valid.values[-1] == 0] = np.nan
        result = pd.Series(-corr, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(3, 1).mean() / temp_result.rolling(3, 1).std()
        return alpha
