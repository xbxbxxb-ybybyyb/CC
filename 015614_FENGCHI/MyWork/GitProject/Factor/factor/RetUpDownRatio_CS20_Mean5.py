# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.FixUtil import minute_data_transform,min_forward_adj
from xfactor.BaseFactor import BaseFactor


class RetUpDownRatio_CS20_Mean5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute"]
    m = 20
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_close = min_forward_adj(minute_close)
        minute_ret = minute_close.pct_change(periods=1)
        minute_ret_cs = minute_ret.iloc[-self.m:]
        ret_cs_up = minute_ret_cs[minute_ret_cs > 0].sum()
        ret_cs_down = -minute_ret_cs[minute_ret_cs < 0].sum()
        ret_up_down = ret_cs_up / ret_cs_down
        return -ret_up_down

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
