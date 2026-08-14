from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VwapStdCorrBias20d_13h(BaseFactor):

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    minute_lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        MinuteTurnover = a.groupby(pd.Grouper(freq='5min')).sum()
        MinuteVolume = v.groupby(pd.Grouper(freq='5min')).sum()
        vwap = MinuteTurnover/MinuteVolume
        re = c / c.shift() - np.ones(c.shape)
        sd = re.groupby(pd.Grouper(freq='5min')).std()
        return Util.array_coef(vwap, sd)

    def reform(self, temp):
        return -(temp-temp.rolling(20).mean())/temp.rolling(20).std()