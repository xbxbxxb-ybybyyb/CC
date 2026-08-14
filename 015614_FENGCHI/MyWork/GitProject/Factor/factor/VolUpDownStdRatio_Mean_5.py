# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
import numpy as np


class VolUpDownStdRatio_Mean_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.close_minute",
                   "FactorData.Basic_factor.volume_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_open = database.depend_data['FactorData.Basic_factor.open_minute']
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_ret = minute_close / minute_open - 1
        volume_positive = minute_volume * (minute_ret > 0)
        volume_negative = minute_volume * (minute_ret < 0)
        volume_positive[volume_positive == 0] = np.nan
        volume_negative[volume_negative == 0] = np.nan
        volume_positive_std = volume_positive.std(axis=0)
        volume_negative_std = volume_negative.std(axis=0)
        ans = volume_positive_std / volume_negative_std
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
