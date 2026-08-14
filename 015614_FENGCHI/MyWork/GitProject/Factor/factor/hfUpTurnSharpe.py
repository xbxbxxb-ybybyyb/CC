import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfUpTurnSharpe(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.float_a_shares']
    lag = 1
    reform_window = 30
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        fas = database.depend_data['FactorData.Basic_factor.float_a_shares']

        stk_code = vol.columns.union(fas.columns)
        vol, amt, fas = vol.reindex(columns=stk_code), amt.reindex(columns=stk_code), fas.reindex(columns=stk_code)
        vol, amt = vol.values[120:], amt.values[120:]
        fas = fas.values[0]
        vwap = amt / vol
        vol_rs = np.where(vwap[1:] > vwap[:-1], vol[1:], np.nan)
        turn = vol_rs / fas
        result = pd.Series(np.nanmean(turn, axis=0), index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(30, 5).mean() / temp_result.rolling(30, 5).std()
        return alpha
