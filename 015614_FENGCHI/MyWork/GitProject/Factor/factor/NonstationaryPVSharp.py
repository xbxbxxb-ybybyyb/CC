# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd

class NonstationaryPVSharp(BaseFactor):
    
    """
    *因子名 : NonstationaryPVSharp
    *因子功能描述 : 非平稳时间序列量价相关性的sharp
                
    *因子参数 : volume, close_adj,is_valid 
    *作者 : 肖倩
    *因子创建日期 : 2018.01.21
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    """ 
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume", "FactorData.Basic_factor.close_badj","FactorData.Basic_factor.is_valid"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    reform_window = 5

    def calc_single(self, database):

        volume = database.depend_data['FactorData.Basic_factor.volume']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        n = 5
        non_corr = self.nonstationary_corr(volume,close_adj)#[is_valid==1]
        is_valid_tf = pd.DataFrame(is_valid.values>0, index=is_valid.index,
            columns=is_valid.columns)
        non_corr = non_corr[is_valid_tf.iloc[-1,:]]
        # non_corr_sharp = self.sharp(non_corr,n)
        return non_corr

    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
        return A
    
    # def sharp(self,factor,n):

    #     res = factor.rolling(n).mean()/factor.rolling(n).std()
    #     return res
    def nonstationary_corr(self,x,y,t=5):

        # Ax = self.A_compute(x,x,t)
        # Ax = np.sqrt(Ax)
        # Ay = self.A_compute(y,y,t)
        # Ay = np.sqrt(Ay)
        # Axy = self.A_compute(x,y,t)
        # alpha = Axy/(Ax*Ay)
        alpha = self.A_compute(x,y,t) / np.sqrt(self.A_compute(x,x,t) * self.A_compute(y,y,t))
        return -alpha

    def A_compute(self,x,y,t=5):
        # x_pre = x.shift(1)
        # Ax = x-x_pre
        # y_pre = y.shift(1)
        # Ay = y-y_pre
        A = (x - x.shift(1)) * (y - y.shift(1))
        # A = A.rolling(t).mean()
        A = A.iloc[-t:,:].mean()
        return A