# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.FixUtil import min_forward_adj
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class Ret2Drawdown_CS60_Mean2Std10(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    m = 60
    reform_window = 10

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_close = min_forward_adj(minute_close)
        ret_cs = minute_close.iloc[-1] / minute_close.iloc[-self.m] - 1
        drawdown_cs = minute_close.iloc[-self.m] / minute_close.min(axis=0) - 1
        ret_dd_ratio = ret_cs / drawdown_cs
        return -ret_dd_ratio

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
