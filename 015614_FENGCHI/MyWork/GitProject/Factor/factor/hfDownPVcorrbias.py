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


class hfDownPVcorrbias(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']
    reform_window = 10
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = vol.columns
        vol, amt = vol.values, amt.values
        vwap = amt / vol
        vwap_last = np.roll(vwap, 1, axis=0)
        vwap_last[0] = np.nan
        rs_flag = vwap < vwap_last
        vol_rs = np.where(rs_flag, vol, np.nan)
        vwap_rs = np.where(rs_flag, vwap, np.nan)
        result = array_corr_np(vol_rs, vwap_rs)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -((temp_result - temp_result.rolling(5, 1).mean()) / temp_result.rolling(5).std()).rolling(5, 1).mean()
        return alpha
