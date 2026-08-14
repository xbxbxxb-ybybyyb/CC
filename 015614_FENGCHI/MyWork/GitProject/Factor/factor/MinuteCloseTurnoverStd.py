# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
class MinuteCloseTurnoverStd(BaseFactor):

    """

    *因子名 : MinuteCloseTurnoverStd
    *因子功能描述 : 计算尾盘换手率波动,波动越小越好
    *因子参数 : *
    *函数返回值 : MinuteCloseTurnoverStd
    *作者 : 孙海平
    *因子创建日期 : 2019.4.16
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """    
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.free_float_shares", \
    "FactorData.Basic_factor.close"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']*1e4
        close = database.depend_data['FactorData.Basic_factor.close']
        free_float_cap = free_float_shares*close

        fmt = '%Y-%m-%d'
        date = np.unique(MinuteTurnover.index.strftime(fmt))[0]                

        Turnover = MinuteTurnover.loc[date]
        
        length = 30                
        factor = Turnover[-length:]/free_float_cap.iloc[-1]
        factor[np.isinf(factor)] = np.nan
        factor.fillna(0,inplace=True)    
        alpha = -factor.std()  

        return alpha


