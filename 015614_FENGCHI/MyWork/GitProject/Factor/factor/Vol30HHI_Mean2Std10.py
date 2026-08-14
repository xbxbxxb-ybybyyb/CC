# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

import numpy as np


class Vol30HHI_Mean2Std10(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    reform_window = 10

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_volume_30 = minute_volume.resample('30T').sum()
        vol_sum_squared = np.square(minute_volume_30.sum(axis=0))
        vol_squared = np.square(minute_volume_30)
        hhi = (vol_squared / vol_sum_squared).sum(axis=0)
        return hhi

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
