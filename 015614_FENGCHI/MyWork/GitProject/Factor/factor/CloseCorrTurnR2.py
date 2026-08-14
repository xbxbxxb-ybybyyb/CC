# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

class CloseCorrTurnR2(BaseFactor):
    """

    *因子名 : CloseCorrTurnR2
    *因子功能描述 : 量价齐飞因子变形，采用20日收盘价与换手率的线性回归的R2作为因子
                     
    *因子参数 : close_adj-调整收盘价，turn-换手率，is_valid_raw-是否合法
    *作者 : wulb
    *因子创建日期 : 2019.1.29
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    factor_type = "DAY"

    s_close_badj = 'FactorData.Basic_factor.close_badj'
    s_turn = 'FactorData.Basic_factor.turn'

    depend_data = [s_close_badj, s_turn]
    n = 20
    lag = n-1

    def calc_single(self, database):
        close_adj = database.depend_data[self.s_close_badj]
        turn = database.depend_data[self.s_turn]
        fly = Util.array_coef(close_adj, turn)
        factor = - fly * fly
        return factor

        
    
            