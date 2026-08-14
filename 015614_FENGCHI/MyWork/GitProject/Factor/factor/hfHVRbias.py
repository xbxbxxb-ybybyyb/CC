import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfHVRbias(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']
    factor_type = 'FIX'
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = vol.columns
        vol, amt = vol.values, amt.values
        vwap = amt / vol
        vrs_flag = vol >= np.nanquantile(vol, 0.9, axis=0)
        result = np.nanmean(np.where(vrs_flag, vwap, np.nan), axis=0) / np.nanmean(vwap, axis=0)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -((temp_result - temp_result.rolling(5).mean()) / temp_result.rolling(5).std()).rolling(5, 1).mean()
        return alpha
