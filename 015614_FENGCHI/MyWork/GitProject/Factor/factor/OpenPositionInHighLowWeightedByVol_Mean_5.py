# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class OpenPositionInHighLowWeightedByVol_Mean_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.open_minute","FactorData.Basic_factor.high_minute",
                   "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_open = database.depend_data['FactorData.Basic_factor.open_minute']
        minute_high = database.depend_data['FactorData.Basic_factor.high_minute']
        minute_low = database.depend_data['FactorData.Basic_factor.low_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        open_price = minute_open.iloc[0, :]
        buy_sell_strength = (minute_high.max(axis=0) - open_price) / (minute_high.max(axis=0) - minute_low.min(axis=0))
        buy_sell_strength_weighted_by_volume = (buy_sell_strength * minute_volume).sum(axis=0) / minute_volume.sum(axis=0)
        return -buy_sell_strength_weighted_by_volume

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
