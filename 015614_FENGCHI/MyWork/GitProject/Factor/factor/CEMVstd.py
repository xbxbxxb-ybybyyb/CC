from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np

class CEMVstd(BaseFactor):
    
    '''
    * 因子名：CEMVstd
    * 逻辑：该因子是之前因子EMVA使用收盘价改进后的波动率，是一种大幅震荡放量后的反转效应
    * 因子参数：日频数据价量
    * 作者：陈卓
    * 日期：2019.4.3
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.high","FactorData.Basic_factor.low","FactorData.Basic_factor.amt",\
    "FactorData.Basic_factor.adjfactor"]    
    lag = 20     
    reform_window = 20
    def calc_single(self, database):
        high = database.depend_data['FactorData.Basic_factor.high']
        low = database.depend_data['FactorData.Basic_factor.low']
        close = database.depend_data['FactorData.Basic_factor.close']
        amt = database.depend_data['FactorData.Basic_factor.amt']        
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']        
        
        # 提取数据并除以均值
        hp_valid = high*adjfactor
        lp_valid = low*adjfactor
        close_valid = close*adjfactor
        amt_valid = amt
        close_valid = close_valid / close_valid.rolling(window=self.lag, min_periods=self.lag).mean()
        hp_valid = hp_valid / hp_valid.rolling(window=self.lag, min_periods=self.lag).mean()
        lp_valid = lp_valid / lp_valid.rolling(window=self.lag, min_periods=self.lag).mean()
        amt_valid = amt_valid / amt_valid.rolling(window=self.lag, min_periods=self.lag).mean()
        C = hp_valid - lp_valid
        emva = (close_valid - close_valid.shift(1)) * C * amt_valid
        return emva.iloc[-1,:]
    def reform(self, temp_result):
        # 计算n日波动率
        alpha = -temp_result.rolling(self.reform_window, min_periods=5).std()
        return alpha
