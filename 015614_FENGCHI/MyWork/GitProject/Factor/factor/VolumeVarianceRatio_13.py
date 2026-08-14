from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VolumeVarianceRatio_13(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        volume_3min = v.resample('3T').sum()
        volume_10min = v.resample('10T').sum()
        temp1 = (volume_3min).var() / 3.0
        temp2 = (volume_10min).var() / 10.0
        ratio = temp1 / temp2
        return ratio