# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
import numpy as np
from xfactor.FixUtil import minute_data_transform


class UpHigh2VwapWeightedByVolume_SR20(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.volume_minute",
                   "FactorData.Basic_factor.amt_minute"]
    reform_window = 20

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_high = database.depend_data['FactorData.Basic_factor.high_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        minute_vwap = minute_amt / minute_volume
        high_to_vwap = minute_high / minute_vwap - 1
        vol_rise = minute_volume[minute_vwap > minute_vwap.shift(1)]
        vol_rise_flag = (vol_rise >= vol_rise.quantile(0.9))
        vrs_volume = minute_volume[vol_rise_flag]
        vrs_vwap_to_low = high_to_vwap[vol_rise_flag]
        vwap_to_low_weighted_by_volume = (vrs_vwap_to_low * vrs_volume / vrs_volume.sum()).sum()
        return vwap_to_low_weighted_by_volume

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
