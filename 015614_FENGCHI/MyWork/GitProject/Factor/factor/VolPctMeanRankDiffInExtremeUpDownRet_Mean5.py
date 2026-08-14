# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import numpy as np


class VolPctMeanRankDiffInExtremeUpDownRet_Mean5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_ret = minute_close.pct_change(periods=1)
        minute_vol_pct = minute_volume.pct_change(periods=1)
        up_ret = minute_ret.mean() + 2 * minute_ret.std()
        down_ret = minute_ret.mean() - 2 * minute_ret.std()
        up_vol_pct_mean_rank = minute_vol_pct[minute_ret > up_ret].mean().rank(pct=True)
        down_vol_pct_mean_rank = minute_vol_pct[minute_ret < down_ret].mean().rank(pct=True)
        rank_diff = up_vol_pct_mean_rank - down_vol_pct_mean_rank
        return -rank_diff

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
