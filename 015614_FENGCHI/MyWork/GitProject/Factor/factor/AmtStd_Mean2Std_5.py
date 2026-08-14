# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class AmtStd_Mean2Std_5(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    reform_window = 5

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        ans = -minute_amt.std()
        return -ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
