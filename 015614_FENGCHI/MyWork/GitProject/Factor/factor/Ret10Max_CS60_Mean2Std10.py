# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class Ret10Max_CS60_Mean2Std10(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    m = 60
    reform_window = 10

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_ret10 = minute_close.pct_change(periods=10)
        minute_ret10_cs = minute_ret10.iloc[-self.m:, ]
        ret10_max = minute_ret10_cs.max()
        return ret10_max

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
