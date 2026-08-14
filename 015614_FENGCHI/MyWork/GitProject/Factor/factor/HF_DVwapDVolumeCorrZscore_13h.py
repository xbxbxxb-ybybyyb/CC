from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_DVwapDVolumeCorrZscore_13h(BaseFactor):

    """
    * 因子名：HF_DVwapDVolumeCorrZscore_13h
    * 因子功能描述：Vwap变化量与Volume变化量的相关系数，取负号，取Zscore。代表日内缩量上涨或放量下跌的股票信息不对称程度高。
    * 因子参数：MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.8.16
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20


    """ 
    """
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']  

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        volume = MinuteVolume.loc[compute_date]
        vwap = MinuteTurnover.loc[compute_date] / volume        
        vwap_df = vwap - vwap.shift()
        volume_df = volume - volume.shift()
        corr = Util.array_coef(vwap_df,volume_df)
        
        return -1*corr

    def reform(self, factor):
        factor = self.zscore(factor,window=self.reform_window)
        return factor        


    def rolling_mean(self,factor,window):
        return factor.rolling(window=window,min_periods=1).mean()
    
    def rolling_std(self,factor,window):
        return factor.rolling(window=window,min_periods=1).std()
    
    def zscore(self,factor,window=5):
        return (factor-self.rolling_mean(factor,window=window)) / self.rolling_std(factor,window=window)
