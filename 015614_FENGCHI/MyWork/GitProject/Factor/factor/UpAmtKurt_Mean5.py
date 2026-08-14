# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import numpy as np


class UpAmtKurt_Mean5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        minute_ret = minute_close.pct_change(periods=1)
        minute_amt_ewm = minute_amt.ewm(span=10).mean()
        up_amt_kurt = minute_amt_ewm[minute_ret > 0].kurt()
        return -up_amt_kurt

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
