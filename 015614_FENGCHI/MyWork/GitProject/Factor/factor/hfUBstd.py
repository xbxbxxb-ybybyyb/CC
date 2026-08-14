import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfUBstd(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_adj_minute', 'FactorData.Basic_factor.volume_adj_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.low_adj_minute']
    factor_type = 'FIX'
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        low = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        stk_code = close.columns
        close, vol, amt, low = close.values[-240:], vol.values[-240:], amt.values[-240:], low.values[-240:]
        vwap = amt / vol
        price_ratio = close / low - 1
        rs_flag = vwap[1:] > vwap[:-1]
        vol_rs = np.where(rs_flag, vol[1:], np.nan)
        vrs_flag = vol_rs >= np.nanquantile(vol_rs, 0.9, axis=0)
        result = np.nanmean(np.where(vrs_flag, price_ratio[1:], np.nan), axis=0)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -temp_result.rolling(5, 1).std()
        return alpha
