import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfRST(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.high_minute']
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        stk_code = close.columns
        close, vol, amt, high = close.values, vol.values, amt.values, high.values
        vwap = amt / vol
        price_ratio = high / close - 1
        rs_flag = vwap[1:] > vwap[:-1]
        rs_vol = np.where(rs_flag, vol[1:], np.nan)
        vrs_flag = rs_vol >= np.nanquantile(rs_vol, 0.9, axis=0)
        result = np.nanmean(np.where(vrs_flag, price_ratio[1:], np.nan), axis=0)
        result = pd.Series(-result, index=stk_code)
        return result
