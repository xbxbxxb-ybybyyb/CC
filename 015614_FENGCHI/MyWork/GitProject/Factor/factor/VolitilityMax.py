from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np

class VolitilityMax(BaseFactor):
    """

    *因子名 : VolitilityMax
    *因子功能描述 : 计算相对最大波动因子，即股票当日最大波动相对市场多均线波动率
    *因子参数 : close_adj-收盘价 open_adj-开盘价 is_valid-是否合法
    *函数返回值 : 相对最大波动因子
    *作者 : 孙海平
    *因子创建日期 : 2019.2.18
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """        
    factor_type = "DAY"
    s_high_badj = 'FactorData.Basic_factor.high_badj'
    s_low_badj = 'FactorData.Basic_factor.low_badj'
    s_open_market = 'FactorData.Basic_factor.open-000001.SH'
    s_close_market = 'FactorData.Basic_factor.close-000001.SH'
    depend_data = [s_high_badj, s_low_badj, s_open_market, s_close_market]
    n = 60
    reform_window = n * 4
    def calc_single(self, database):
        open_market = database.depend_data[self.s_open_market].iloc[-1]
        close_market = database.depend_data[self.s_close_market].iloc[-1]
        low_adj = database.depend_data[self.s_low_badj].iloc[-1]
        high_adj = database.depend_data[self.s_high_badj].iloc[-1]
        diff_j_max = (high_adj-low_adj)/low_adj
        diff_real_market = (close_market.values- open_market.values)/close_market.values
        volitility2 = (diff_j_max.values - diff_real_market[0])#/market_return.values
        volitility2 = pd.Series(data=volitility2,name=high_adj.name,index=high_adj.index)

        # base = (volitility2.rolling(window=n*2).std()+volitility2.rolling(window=n*3).std()+volitility2.rolling(window=n*4).std())/3
        # factor5 = -(volitility2.rolling(window=n).std() - base)/base        

        return volitility2
    
    def reform(self, temp_result):
        base = (temp_result.rolling(self.n * 2).std() 
            + temp_result.rolling(self.n * 3).std()
            + temp_result.rolling(self.n * 4).std()) / 3
        return -(temp_result.rolling(self.n).std() - base) / base
    