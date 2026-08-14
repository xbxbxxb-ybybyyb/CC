# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class RetSkew_Mean_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.close_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_open = database.depend_data['FactorData.Basic_factor.open_minute']
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_ret = minute_close / minute_open - 1
        minute_ret_skew = minute_ret.skew(axis=0)
        return -minute_ret_skew

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
