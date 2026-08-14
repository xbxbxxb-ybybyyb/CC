# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class CorrCloseVol_Std_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    m = 20
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        corr_close_volume = minute_close.corrwith(minute_volume, axis=0)
        return -corr_close_volume

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).std()
