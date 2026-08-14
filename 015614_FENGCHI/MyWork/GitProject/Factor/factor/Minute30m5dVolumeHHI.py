import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class Minute30m5dVolumeHHI(BaseFactor):
    depend_data = ['FactorData.Basic_factor.volume_minute']
    lag = 4

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = vol.columns
        vol = vol.resample('30min').sum().dropna(how='all').values
        result = np.nansum((vol / np.nansum(vol, axis=0)) ** 2, axis=0)
        result = pd.Series(-result, index=stk_code)
        return result
