# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class OverBuySell_Mean_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        close_mean = minute_close.rolling(window=10, min_periods=1).mean()
        close_std = minute_close.rolling(window=10, min_periods=1).std()
        bool_up = close_mean + 2 * close_std
        up_pct = minute_close[minute_close > bool_up] / bool_up - 1
        up_pct_sum = up_pct.sum(axis=0)
        bool_down = close_mean - 2 * close_std
        down_pct = minute_close[minute_close < bool_down] / bool_down - 1
        down_pct_sum = down_pct.sum(axis=0)
        ans = up_pct_sum + down_pct_sum
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
