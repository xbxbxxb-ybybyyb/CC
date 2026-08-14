import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class HF_VwapTailTurnRatioZscore(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.free_float_shares', 'FactorData.Basic_factor.close']
    factor_type = 'FIX'
    lag = 2
    reform_window = 10

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']
        stk_code = vol.columns
        vol = vol.values
        amt = amt.values
        ffc = ffs.values * close.values
        vwap_0 = amt[240:240*2] / vol[240:240*2]
        turn_0 = amt[240:240*2] / ffc[0]
        vwap_1 = amt[240*2:] / vol[240*2:]
        turn_1 = amt[240*2:] / ffc[1]
        vwap = np.concatenate((vwap_0[-30:], vwap_1), axis=0)
        turn = np.concatenate((turn_0[-30:], turn_1), axis=0)
        turn_tail = np.nanmean(np.where(vwap < np.nanquantile(vwap, 0.1, axis=0), turn, np.nan), axis=0)
        result = pd.Series(turn_tail / np.nanmean(turn, axis=0), index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = (temp_result - temp_result.rolling(10, 1).mean()) / temp_result.rolling(10, 1).std()
        return alpha
