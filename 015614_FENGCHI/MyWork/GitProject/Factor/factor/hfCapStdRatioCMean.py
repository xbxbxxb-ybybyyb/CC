import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfCapStdRatioCMean(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high_adj_minute', 'FactorData.Basic_factor.low_adj_minute',
                   'FactorData.Basic_factor.volume_adj_minute', 'FactorData.Basic_factor.amt_minute']
    lag = 1
    reform_window = 60
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        low = database.depend_data['FactorData.Basic_factor.low_adj_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = high.columns
        high, low, vol, amt = high.values[-240:], low.values[-240:], vol.values[-240:], amt.values[-240:]
        vwap = amt / vol
        vwap_last = np.roll(vwap, 1, axis=0)
        vwap_last[0] = np.nan
        rs_flag = vwap > vwap_last
        high_cap = np.where(rs_flag, high * vol, np.nan)
        low_cap = np.where(~rs_flag, low * vol, np.nan)
        part_0 = np.nanstd(high_cap / np.nanmean(high_cap, axis=0), axis=0)
        part_1 = np.nanstd(low_cap / np.nanmean(low_cap, axis=0), axis=0)
        result = part_0 / part_1
        result[np.isinf(result)] = np.nan
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -temp_result / temp_result.rolling(60, 1).mean()
        alpha[np.isinf(alpha)] = np.nan
        return alpha
