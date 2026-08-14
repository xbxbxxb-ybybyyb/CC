# -*- coding: utf-8 -*-
"""
@author: 011668
"""

from xfactor.BaseFactor import BaseFactor


class FreeturnRankUpDownRatio_CS30(BaseFactor):
    factor_type = 'DAY'  # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.free_float_shares",
                   "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    m = 30
    p = 0.2

    def calc_single(self, database):
        # 播放的数据通过self.data_base_play字典获取
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        minute_ret = minute_close.pct_change(periods=1)
        minute_ret_cs_rank = minute_ret.iloc[-self.m:, ].rank(pct=True)
        free_turn = minute_volume.div(free_float_shares.loc[free_float_shares.index[-1]], axis=1)
        free_turn_cs = free_turn.iloc[-self.m:, ]
        free_turn_up = free_turn_cs[minute_ret_cs_rank > 1-self.p].mean()
        free_turn_down = free_turn_cs[minute_ret_cs_rank < self.p].mean()
        free_turn_up_down_ratio = free_turn_up / free_turn_down
        return -free_turn_up_down_ratio
