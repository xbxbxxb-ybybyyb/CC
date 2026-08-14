"""
    *因子名 : PVSwingCorr
    *因子功能描述 : 当日开盘到十一点半分钟价量与分钟振幅相关性。相关性越小表示价量受振幅影响越小，投机行为越弱，获取超额概率更大。

    *因子参数 : MinuteVolume -- 分钟成交量, MinuteLow -- 分钟最低价, MinuteHigh -- 分钟最高价, MinuteTurnover -- 分钟成交额
    *作者 : 徐志鑫
    *因子创建日期 : 2019.07.09
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
"""
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class PVSwingCorr(BaseFactor):
    
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute','FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation=["drop","merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']

        fmt = '%Y-%m-%d'
        dates = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        today = dates[-1]
        
        today_turnover = MinuteTurnover.loc[today]
        today_volume = MinuteVolume.loc[today]
        today_price = today_turnover / today_volume

        low = MinuteLow.loc[today]
        high = MinuteHigh.loc[today]
        
        swing = (high - low) / low
        
        corr = Util.array_coef(today_price,swing) + Util.array_coef(today_volume,swing)
        
        return -corr

    # def definition(self, MinuteVolume, MinuteLow, MinuteHigh, MinuteTurnover):
    #     corr = self.minute_help(self.minute, 'PVSwingCorr_13hHelp', MinuteVolume, MinuteLow, MinuteHigh, MinuteTurnover)
    #     return corr

    # def minute(self, MinuteVolume, MinuteLow, MinuteHigh, MinuteTurnover):
    #     fmt = '%Y-%m-%d'
    #     dates = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
    #     today = dates[-1]
        
    #     today_turnover = MinuteTurnover.loc[today]
    #     today_volume = MinuteVolume.loc[today]
    #     today_price = today_turnover / today_volume

    #     low = MinuteLow.loc[today]
    #     high = MinuteHigh.loc[today]
        
        # swing = (high - low) / low
        
        # corr = today_price.corrwith(swing) + today_volume.corrwith(swing)
        
        # return -corr
