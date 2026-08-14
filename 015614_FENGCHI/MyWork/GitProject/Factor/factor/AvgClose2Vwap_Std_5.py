# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class AvgClose2Vwap_Std_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        close_average = minute_close.mean(axis=0)
        vwap = (minute_amt.sum(axis=0) / minute_volume.sum(axis=0))
        ans = close_average / vwap
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).std()
