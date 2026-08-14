import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfDownStrength(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.high_minute',
                   'FactorData.Basic_factor.low_minute']
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        stk_code = close.columns
        close, vol, amt, high, low = close.values, vol.values, amt.values, high.values, low.values
        vwap = amt / vol
        vwap_last = np.roll(vwap, 1, axis=0)
        vwap_last[0] = np.nan
        price_ratio = (high - low) / (close - low + 0.001)
        rs_flag = vwap < vwap_last
        vol_rs = np.where(rs_flag, vol, np.nan)
        vrs_flag = vol_rs >= np.nanquantile(vol_rs, 0.9, axis=0)
        result = np.nanmean(np.where(vrs_flag, price_ratio, np.nan), axis=0)
        result = pd.Series(-result, index=stk_code)
        return result
