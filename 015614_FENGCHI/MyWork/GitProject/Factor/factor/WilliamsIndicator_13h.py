from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class WilliamsIndicator_13h(BaseFactor):
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        o = database.depend_data['FactorData.Basic_factor.open_minute']
        h = database.depend_data['FactorData.Basic_factor.high_minute']
        l = database.depend_data['FactorData.Basic_factor.low_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        indicator = -(h.max() - o.iloc[-1]) / (h.max() - l.min())
        return indicator
