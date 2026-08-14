from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VwapAmtCorrMean5d_13h(BaseFactor):
    '''
    负向， vwap与成交额的过去4天的相关性
    '''
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_adj_minute", "FactorData.Basic_factor.amt_minute"]
    lag = 0
    minute_lag = 4
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        return Util.array_coef(a / v, a)

    def reform(self, temp):
        def decay(x):
            period = len(x)
            decay_days = 5.0
            w = np.array([pow(pow(1/2,1/decay_days), period - 1 - i) for i in range(period)])
            w= w/w.sum()
            return np.sum(w*x)
        return -temp.rolling(20,min_periods=20).apply(decay)
