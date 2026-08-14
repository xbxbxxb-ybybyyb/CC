import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class SplitStdRatio(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = amt.columns
        amt = amt.values
        vol = vol.values
        vwap = amt / vol
        vwap_last = np.roll(vwap, 1, axis=0)
        vwap_last[0] = np.nan
        re = vwap / vwap_last - 1
        vwap_now = np.nanmean(vwap[-5:], axis=0)
        std_h = np.nanstd(np.where(vwap > vwap_now, re, np.nan), axis=0)
        std_l = np.nanstd(np.where(vwap < vwap_now, re, np.nan), axis=0)
        result = pd.Series(std_l / std_h, index=stk_code)
        return result
