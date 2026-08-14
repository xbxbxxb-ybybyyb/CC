# -*- coding: utf-8 -*-
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd


class HighLowMeanVwapRetSharpe(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        stk_code = high.columns
        high = high.expanding().mean().values
        low = low.expanding().mean().values
        vwap = amt.cumsum().values / vol.cumsum().values
        r = (high + low) / 2 / vwap - 1
        a = np.arange(1, len(r) + 1)
        a = (a / a.sum()).reshape(len(a), 1)
        m = np.nansum(r * a, axis=0)
        s = np.nansum((r - m) ** 2, axis=0) ** 0.5
        result = pd.Series(m / s, index=stk_code)
        return result
