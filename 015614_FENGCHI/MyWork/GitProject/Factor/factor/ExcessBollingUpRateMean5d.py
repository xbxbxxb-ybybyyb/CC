from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class ExcessBollingUpRateMean5d(BaseFactor):
    factor_type = "FIX"
    s_close_min = 'FactorData.Basic_factor.close_minute'
    depend_data = [s_close_min]
    reform_window = 5
    def calc_single(self, database):
        minute_data_transform(database.depend_data)
        close_min = database.depend_data[self.s_close_min]
        return self.minute(close_min)

    def reform(self, temp_result):
        return  -temp_result.rolling(self.reform_window).mean()

    def minute(self,MinuteClose):
        # fmt = '%Y-%m-%d'
        # date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        close_min_std = MinuteClose.std()
        up = MinuteClose.mean(axis=0) + close_min_std.values * 2
        # print(up.shape)
        excess_rate =(MinuteClose.values - up.values) / up.values
        # print(excess_rate.shape)
        excess_rate[excess_rate < 0] = 0
        return pd.DataFrame(excess_rate, index = MinuteClose.index, columns = MinuteClose.columns).sum()
        