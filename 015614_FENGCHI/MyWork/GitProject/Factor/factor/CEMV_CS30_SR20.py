# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform, min_forward_adj


class CEMV_CS30_SR20(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute",
                   "FactorData.Basic_factor.volume_minute"]
    m = 30
    reform_window = 20

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_high = database.depend_data['FactorData.Basic_factor.high_minute']
        minute_high = min_forward_adj(minute_high)
        minute_low = database.depend_data['FactorData.Basic_factor.low_minute']
        minute_low = min_forward_adj(minute_low)
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        high_mean = minute_high / minute_high.mean()
        low_mean = minute_low / minute_low.mean()
        vol_mean = minute_volume / minute_volume.mean()
        price_range = high_mean - low_mean
        mid_price = (high_mean + low_mean) / 2
        mid_price_diff = mid_price.pct_change(periods=1)
        ans = (vol_mean.iloc[-self.m:] * price_range.iloc[-self.m:] * mid_price_diff.iloc[-self.m:]).mean()
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
