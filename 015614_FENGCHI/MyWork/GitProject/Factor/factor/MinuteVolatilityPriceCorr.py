# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


"""
    * 因子名：MinuteVolatilityPriceCorr_13h
    * 因子功能描述：当日价格分钟线5分钟波动率与价格的相关性，相关性越低，说明异常炒作越少，具备较为稳定的超额能力
    * 因子参数：  MinuteClose
    * 作者：刘道一
    * 因子创建日期： 20190628
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""
class MinuteVolatilityPriceCorr(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute']    
    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 5
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])

        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        compute_date = date_list[-1]
        
        close_df = MinuteClose.loc[compute_date]
        
        price_std = close_df.rolling(5).std().iloc[5:]
        
        # result = price_std.corrwith(close_df.iloc[5:])
        result = Util.array_coef(price_std, close_df.iloc[5:])
                
        return result

    def reform(self, temp_result):
        for i in range(len(temp_result)):
            if len(temp_result.iloc[i].dropna())==0:temp_result.iloc[i] = 0.
        return -1*temp_result


    # def definition(self, MinuteClose):
    #     result = self.minute_help(self.minute, 'MinuteVolatilityPriceCorr_13hHelp', MinuteClose)
    #     for i in range(len(result)):
    #         if len(result.iloc[i].dropna())==0:result.iloc[i] = 0.
    #     return -1*result

    # def minute(self, MinuteClose):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     compute_date = date_list[-1]
    #     close_df = MinuteClose.loc[compute_date]
        
    #     price_std = close_df.rolling(5).std().iloc[5:]
        
    #     result = price_std.corrwith(close_df.iloc[5:])
                
    #     return result

