# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
class HighFreqRelativeTurnoverStd(BaseFactor):
     # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_adj_minute","FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 1
    reform_window=5
    # fix_times=["1300"] 
    def calc_single(self,database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        factor = -self.minute_help( MinuteClose,MinuteTurnover)
        return factor
    def reform(self,temp_result):
        factor = temp_result
        n = 5
        res = -(factor.rolling(window=n,min_periods=3).mean())/(factor.rolling(window=n,min_periods=3).std())
        return res

    def minute_help(self,MinuteTurnover,MinuteClose):        
        def filter(data):
            data[data<=data.mean()] = np.nan
            return data

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]                
        
        close = MinuteClose.loc[compute_date]  
        turnover = MinuteTurnover.loc[compute_date]  

        close_pre = MinuteClose.loc[pre_date]
        turnover_pre = MinuteTurnover.loc[pre_date]     
        
        close = close_pre.append(close)
        turnover = turnover_pre.append(turnover)     

          # 趋势指标
        ret = pd.DataFrame(close.values/close.shift(1).values-1,index=close.index,columns=close.columns)
        ret_abs = abs(ret).rolling(window=5).mean()
        ret_mean = ret.rolling(window=5).mean()
        trend_ret = ret_abs/ret_mean
        trend_ret[np.isinf(trend_ret.values)] = np.nan 

        # 趋势明显时的成交量
        trend_ret =  trend_ret.apply(filter)
        turnover_ = copy.deepcopy(turnover)
        turnover_[np.isnan(trend_ret.values)] = 0
        turnover_std = turnover.std()/turnover_.std()

        return turnover_std