import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfTurnSharpeHD(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_adj_minute', 'FactorData.Basic_factor.float_a_shares',
                   'FactorData.Basic_factor.amt_minute']
    lag = 1
    reform_window = 20
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        fas = database.depend_data['FactorData.Basic_factor.float_a_shares']
        stk_code = vol.columns
        vol, amt, fas = vol.values[-240:], amt.values[-240:], fas.values[0]
        vwap = amt / vol
        vol = amt / vwap
        turn = vol / fas
        result = pd.Series(np.nanmean(turn, axis=0), index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(20, 5).mean() / temp_result.rolling(20, 5).std()
        return alpha
