# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class RetSkew_CS180_Mean2Std30(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    m = 180
    reform_window = 30

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_ret = minute_close.pct_change(periods=1)
        minute_ret_cs = minute_ret.iloc[-self.m:]
        ret_skew_cs = minute_ret_cs.skew(axis=0)
        return -ret_skew_cs

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
