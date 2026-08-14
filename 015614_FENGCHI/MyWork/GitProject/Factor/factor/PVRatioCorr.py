import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj

"""
    *因子名 : PVRatioCorr
    *因子功能描述 : 开盘到上午收盘，分钟成交量和分钟均价，与上个交易日同时段分钟成交量和分钟均价之比，计算两个比值相关性。表示价和量增长的相关程度，相关性越小超额越大。

    *因子参数 : MinuteVolume -- 分钟成交量, MinuteTurnover -- 分钟成交额, adjfactor -- 复权因子
    *作者 : 徐志鑫
    *因子创建日期 : 2019.07.31
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
"""

class PVRatioCorr(BaseFactor):
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_adj_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series    
    
    def calc_single(self, database):
        
        minute_data_transform(database.depend_data, operation=["drop","merge"])

        fmt = '%Y-%m-%d'
        dates = sorted(np.unique(database.depend_data['FactorData.Basic_factor.amt_minute'].index.strftime(fmt)))
        
        today = dates[-1]
        last_date = dates[-2]

        today_turnover = database.depend_data['FactorData.Basic_factor.amt_minute'].loc[today]
        today_volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute'].loc[today]

        last_turnover = database.depend_data['FactorData.Basic_factor.amt_minute'].loc[last_date].iloc[:120]
        last_volume = database.depend_data['FactorData.Basic_factor.volume_adj_minute'].loc[last_date].iloc[:120]

        today_price = today_turnover / today_volume
        last_price = last_turnover / last_volume
        
        today_volume = today_volume.reset_index(drop=True)
        last_volume = last_volume.reset_index(drop=True)
        today_price = today_price.reset_index(drop=True)
        last_price = last_price.reset_index(drop=True)
        
        volume_ratio = today_volume / last_volume
        volume_ratio[np.isinf(volume_ratio)] = np.nan
        price_ratio = today_price / last_price
        price_ratio[np.isinf(price_ratio)] = np.nan
        
        # corr = price_ratio.corrwith(volume_ratio)
        corr = Util.array_coef(price_ratio, volume_ratio)
        return -corr

    # def definition(self, MinuteVolume, MinuteTurnover, adjfactor):
    #     corr = self.minute_help(self.minute, 'PVRatioCorr_13hHelp', MinuteVolume, MinuteTurnover, adjfactor)
    #     return corr
        
    # def minute(self, MinuteVolume, MinuteTurnover, adjfactor):
    #     fmt = '%Y-%m-%d'
    #     dates = sorted(np.unique(MinuteVolume.index.strftime(fmt)))

    #     today = dates[-1]
    #     last_date = dates[-2]

    #     today_turnover = MinuteTurnover.loc[today]
    #     today_volume = MinuteVolume.loc[today]
    #     last_turnover = MinuteTurnover.loc[last_date].iloc[: 120]
    #     last_volume = MinuteVolume.loc[last_date].iloc[: 120]
        
    #     today_price = (today_turnover / today_volume) * adjfactor.iloc[-1]
    #     last_price = (last_turnover / last_volume) * adjfactor.iloc[-2]
        
    #     today_volume = today_volume.reset_index(drop=True)
    #     last_volume = last_volume.reset_index(drop=True)
    #     today_price = today_price.reset_index(drop=True)
    #     last_price = last_price.reset_index(drop=True)
        
    #     volume_ratio = today_volume / last_volume
    #     volume_ratio[np.isinf(volume_ratio)] = np.nan
    #     price_ratio = today_price / last_price
    #     price_ratio[np.isinf(price_ratio)] = np.nan
        
    #     corr = price_ratio.corrwith(volume_ratio)
    #     return -corr
        
        
        
        
        
