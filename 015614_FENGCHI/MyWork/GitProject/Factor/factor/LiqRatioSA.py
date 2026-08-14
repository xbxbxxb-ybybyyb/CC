# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor 
import numpy as np

class LiqRatioSA(BaseFactor):
    
    '''
    * 因子名：LiqRatioSA
    * 逻辑：该因子为成交量相对于自由流通股本占比的标准差与均值之比，反映股票的流动性和关注度和波动情况
    * 因子参数：成交量（单位：元），自由流通市值，收盘价，is_valid_raw
    * 作者：xust
    * 日期：2018.12.26
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''

    factor_type = 'DAY'

    # 个股成交量（手）
    s_volume_by_share = 'FactorData.Basic_factor.volume'
    # 流通股数（万股）
    s_free_float_shares = 'FactorData.Basic_factor.free_float_shares'
    depend_data = [s_volume_by_share, s_free_float_shares]

    # rolling窗口（默认: 40d)
    reform_window = 40
    
    def calc_single(self, database):
        volume_by_share = database.depend_data[self.s_volume_by_share]
        free_float_shares = database.depend_data[self.s_free_float_shares]
        return volume_by_share.iloc[-1] / free_float_shares.iloc[-1]

    def reform(self, temp_result):
        n = self.reform_window
        return -temp_result.rolling(window = n).std() / temp_result.rolling(window = n).mean() #反转因子正负号
