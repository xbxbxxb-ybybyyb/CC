import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfDownTurnSharpe(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_adj_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.float_a_shares', 'FactorData.Basic_factor.adjfactor']
    factor_type = 'FIX'
    lag = 1
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        fas = database.depend_data['FactorData.Basic_factor.float_a_shares']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = vol.columns
        vol, amt = vol.values[-240:], amt.values[-240:]
        fas = 10000 * fas.values[0] / adj.values[0]
        vwap = amt / vol
        vwap_last = np.roll(vwap, 1, axis=0)
        vwap_last[0] = np.nan
        rs_flag = vwap < vwap_last
        vol_rs = np.where(rs_flag, vol, np.nan)
        turn = vol_rs / fas
        result = pd.Series(np.nanmean(turn, axis=0), index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(10, 5).mean() / temp_result.rolling(10, 5).std()
        return alpha
