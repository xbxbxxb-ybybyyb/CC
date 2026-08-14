
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_HighPinZscore_13h(BaseFactor):

    """
    * 因子名：HF_HighPinZscore_13h
    * 因子功能描述：通过High与前High大小确定主动买入成交量和主动卖出成交量，两者绝对值差值代表了知情交易者概率。该值越大，股票未来越容易跌。
    * 因子参数：MinuteHigh,MinuteVolume
    * 作者：游加平
    * 因子创建日期： 2019.8.9
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5

    """ 
    """
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']  

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        high = MinuteHigh.loc[compute_date]        
        volume = MinuteVolume.loc[compute_date]        
        volume_buy = volume[high>high.shift()].fillna(0.)
        volume_sell = volume[high<high.shift()].fillna(0.)
        pin = ((volume_sell-volume_buy).abs()).mean() / volume.mean()
        return -pin

    def reform(self, factor):
        factor = self.zscore(factor)
        factor.fillna(0.,inplace=True)         
        return factor         
    
    def rolling_mean(self,factor,window):
        return factor.rolling(window=window).mean()
    
    def rolling_std(self,factor,window):
        return factor.rolling(window=window).std()
    
    def zscore(self,factor,window=5):
        return (factor-self.rolling_mean(factor,window=window)) / self.rolling_std(factor,window=window)
