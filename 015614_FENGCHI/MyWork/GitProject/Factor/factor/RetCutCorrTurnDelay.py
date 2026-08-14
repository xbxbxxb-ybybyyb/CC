# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np

class RetCutCorrTurnDelay(BaseFactor):
    """

    *因子名 : RetCutCorrTurnDelay
    *因子功能描述 : 量价齐飞因子变形，采用10日当日收益率与前一日换手率的相关系数作为因子，剔除当日收益率最高的10%
                     
    *因子参数 : close_adj-调整收盘价，turn-换手率，is_valid_raw-是否合法
    *作者 : wulb
    *因子创建日期 : 2019.1.29
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    # def __init__(self, json_path):
    #     super(RetCutCorrTurnDelay, self).__init__(json_path)

    factor_type = "DAY"
    
    s_pct_chg = 'FactorData.Basic_factor.pct_chg'
    s_turn = 'FactorData.Basic_factor.turn'
    depend_data = [s_pct_chg, s_turn]

    n = 10
    lag = n 

        
    # def definition(self, close_adj, turn, is_valid_raw):
        
    #     n = 10
    #     ret = close_adj.pct_change(1)
    #     ret_rank = ret.rank(pct=True, axis=1)
    #     turn_shift = turn.shift(1)
        
    #     fr_cut = ret[ret_rank < 0.9].rolling(window=n).corr(turn_shift)
    #     fr_cut[is_valid_raw == 0] = np.nan
        
    #     return fr_cut
    
    def calc_single(self, database):
        ret = database.depend_data[self.s_pct_chg].tail(self.n)
        turn = database.depend_data[self.s_turn]
        ret_rank = ret.rank(pct=True, axis=1)
        turn_shift = turn.shift(1).tail(self.n)
        
        fr_cut = ret.values
        fr_cut[(ret_rank.values <= .7) & (ret_rank.values>=.3) ] = np.nan
        fr_cut = Util.array_coef(pd.DataFrame(fr_cut, columns = ret.columns, index = ret.index), turn_shift)

        return fr_cut


        