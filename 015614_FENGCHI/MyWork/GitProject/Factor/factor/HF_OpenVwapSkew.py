import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class HF_OpenVwapSkew(BaseFactor):
    depend_data = ['FactorData.Basic_factor.open_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.volume_minute']
    factor_type = 'FIX'
    lag = 1
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        op = database.depend_data['FactorData.Basic_factor.open_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = op.columns
        op = op.values[180:]
        amt = amt.values[180:]
        vol = vol.values[180:]
        vwap = np.nancumsum(amt, axis=0) / np.nancumsum(vol, axis=0)
        skew = pd.DataFrame(op - vwap, columns=stk_code).skew()
        return skew

    def reform(self, temp_result):
        alpha = -temp_result / temp_result.rolling(20, 1).max()
        alpha[alpha.isnull().all(axis=1)] = 0
        return alpha
