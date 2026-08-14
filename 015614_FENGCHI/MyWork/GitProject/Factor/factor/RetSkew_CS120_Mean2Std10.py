# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class RetSkew_CS120_Mean2Std10(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    m = 120
    reform_window = 10

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_ret = minute_close.pct_change(periods=1)
        minute_ret_cs = minute_ret.iloc[-self.m:]
        ret_skew_cs = minute_ret_cs.skew(axis=0)
        return -ret_skew_cs

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
