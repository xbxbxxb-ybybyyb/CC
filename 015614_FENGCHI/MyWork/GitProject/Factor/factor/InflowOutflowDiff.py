import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def fun(amt, vol):
    r = (amt / vol).pct_change().values
    amt = amt.values
    m = np.nanmedian(amt, axis=0)
    s = np.nanstd(np.where(amt > m, amt, np.nan), axis=0)
    amt_in = np.nansum(np.where((amt > (m + s)) & (r > 0), amt, np.nan), axis=0)
    amt_out = np.nansum(np.where((amt > (m + s)) & (r <= 0), amt, np.nan), axis=0)
    f = (amt_in - amt_out) / np.nansum(amt, axis=0)
    return -np.abs(f - np.nanmean(f))


class InflowOutflowDiff(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']
    factor_type = 'FIX'
    reform_window = 5
    lag = 1
    factor_temp = []

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = amt.columns
        amt_l, amt_t = amt.iloc[:240], amt.iloc[240:]
        vol_l, vol_t = vol.iloc[:240], vol.iloc[240:]
        self.factor_temp.append(fun(amt_l, vol_l))
        self.factor_temp = self.factor_temp[-4:]
        if len(self.factor_temp) == 4:
            f_t = fun(amt_t, vol_t)
            f_l = np.nansum(np.array(self.factor_temp), axis=0)
            result = (f_l + f_t) / 5
        else:
            result = np.nan * np.ones(len(stk_code))
        result = pd.Series(result, index=stk_code)
        return result
