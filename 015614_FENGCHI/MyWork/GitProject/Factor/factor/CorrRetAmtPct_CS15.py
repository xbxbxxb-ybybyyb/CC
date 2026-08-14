# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class CorrRetAmtPct_CS15(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    m = 15

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        minute_data_transform(database.depend_data, operation = ["merge1", "merge1"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        minute_ret = minute_close.pct_change(periods=1)
        minute_amt_pct = minute_amt.pct_change(periods=1)
        minute_ret_cs = minute_ret.iloc[-self.m:]
        minute_amt_pct_cs = minute_amt_pct.iloc[-self.m:]
        corr_ret_amt_pct_cs = minute_ret_cs.corrwith(minute_amt_pct_cs)
        return -corr_ret_amt_pct_cs
