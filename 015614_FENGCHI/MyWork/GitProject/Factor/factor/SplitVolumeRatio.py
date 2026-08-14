import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class SplitVolumeRatio(BaseFactor):
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
        vol[0] = np.nan
        vwap_now = np.nanmean(vwap[-5:], axis=0)
        vol_h = np.nanmean(np.where(vwap > vwap_now, vol, np.nan), axis=0)
        vol_l = np.nanmean(np.where(vwap < vwap_now, vol, np.nan), axis=0)
        result = pd.Series(vol_l / vol_h, index=stk_code)
        return result
