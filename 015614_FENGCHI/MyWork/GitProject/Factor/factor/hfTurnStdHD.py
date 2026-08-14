import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class hfTurnStdHD(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.float_a_shares']
    factor_type = 'FIX'
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        fas = database.depend_data['FactorData.Basic_factor.float_a_shares']
        stk_code = vol.columns
        vol, fas = vol.values[-240:], fas.values[0]
        turn = vol / fas
        result = pd.Series(-np.nanstd(turn, axis=0), index=stk_code)
        return result
