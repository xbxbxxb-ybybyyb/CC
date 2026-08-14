import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteLastHourMDDMCLIMBstd20d(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.is_valid_raw']
    reform_window = 20
    climb_temp = []
    dd_temp = []

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        valid = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        stk_code = close.columns
        close = close.iloc[-60:]
        valid = valid.values[-1]
        dd = -np.nanmin(close.values / close.expanding().max().values - 1, axis=0)
        climb = np.nanmax(close.values / close.expanding().min().values - 1, axis=0)
        dd[valid == 0] = np.nan
        climb[valid == 0] = np.nan
        self.dd_temp.append(dd)
        self.climb_temp.append(climb)
        self.climb_temp = self.climb_temp[-20:]
        self.dd_temp = self.dd_temp[-20:]
        if (len(self.climb_temp) == 20) & (len(self.dd_temp) == 20):
            dd = np.nanstd(np.array(self.dd_temp).astype(np.float64), axis=0)
            climb = np.nanstd(np.array(self.climb_temp).astype(np.float64), axis=0)
            result = dd / climb
            result[np.isinf(result)] = np.nan
            result = pd.Series(result, index=stk_code)
        else:
            result = pd.Series(np.nan, index=stk_code)
        return result
