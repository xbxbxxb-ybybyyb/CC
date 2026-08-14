import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class IbsLast15Min(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']
    factor_type = 'FIX'
    lag = 1
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = high.columns
        high = np.nanmean(high.values[:240][-15:], axis=0)
        low = np.nanmean(low.values[:240][-15:], axis=0)
        vwap = np.nansum(amt.values[:240][-15:], axis=0) / np.nansum(vol.values[:240][-15:], axis=0)
        ibs = pd.Series((high - vwap) / (high - low), index=stk_code)
        return ibs

    def reform(self, temp_result):
        a = np.e ** (-np.log(2) / 2 * np.arange(4, -1, -1))  # 半衰期为2
        a = a / a.sum()
        alpha = temp_result.rolling(5).apply(lambda x: (x * a).sum())
        return alpha
