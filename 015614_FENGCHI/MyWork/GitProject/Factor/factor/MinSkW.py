# -*- coding: utf-8 -*-
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
class MinSkW(BaseFactor):
    factor_type = "DAY"
    reform_window = 10
    depend_data = ["FactorData.Basic_factor.close_minute"]
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        close_df = MinuteClose
        return_df = close_df.pct_change(periods=1)
        skew_last = return_df.iloc[-180:].skew()  # param 120, 60 for skewness
        result_df = skew_last
        return -result_df.rank(pct=True)

    def weight(self,series):
        n = len(series)
        w = np.arange(1, (n + 1), 1) / n
        temp = (series * w).sum()
        return temp
    def reform(self, temp_result):
        return temp_result.rolling(10,5).apply(self.weight)