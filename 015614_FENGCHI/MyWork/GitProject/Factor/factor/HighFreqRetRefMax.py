# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighFreqRetRefMax(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_adj_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 1
    reform_window=10
    # fix_times=["1300"]


    # 最大回撤后的收益/最大回撤
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']       
        factor = self.minute_help( MinuteClose)
        return factor
    
    def reform(self,temp_result):
        factor = temp_result
        n = 10
        res = (factor.rolling(window=n,min_periods=3).mean())/(factor.rolling(window=n,min_periods=3).std())
        return res

    def minute_help(self, MinuteClose):
        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]                
        
        close = MinuteClose.loc[compute_date]  
        
        ret = pd.DataFrame(close.values/close.shift(1).values-1,index=close.index,columns=close.columns)
        ret_mean = ret.mean(axis=1)
                        
        ret_ref_values = ret.values - (ret_mean.values).reshape(-1,1)
        ret_ref = pd.DataFrame(data=ret_ref_values,index=ret.index,columns=ret.columns)
        ret_ref_max = ret_ref.max()

        return ret_ref_max