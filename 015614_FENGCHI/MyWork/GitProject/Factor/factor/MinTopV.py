from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time

class MinTopV(BaseFactor):
    factor_type = 'DAY'
    depend_data = ['FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.amt_minute', ]
    lag = 1
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        volume = volume.replace(0., np.nan)
        vol = volume.values
        am = amt.values
        condition = (vol > np.nanpercentile(vol, 80, axis=0))
        vwap_top = np.nansum(am * condition, axis=0) / np.nansum(vol * condition, axis=0)
        vwap_all = amt.sum() / volume.sum()
        vwap_top = pd.Series(vwap_top, index=volume.columns)
        ratio = vwap_top / vwap_all
        return -ratio
    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,1).apply(self.weight)