# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class RetDiffStd_Mean2Std10(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    reform_window = 10

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_close = minute_close.resample('5T').last()
        minute_ret = minute_close.pct_change(periods=1)
        minute_ret_diff = minute_ret - minute_ret.shift(1)
        minute_ret_diff_std = minute_ret_diff.std()
        return minute_ret_diff_std

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
