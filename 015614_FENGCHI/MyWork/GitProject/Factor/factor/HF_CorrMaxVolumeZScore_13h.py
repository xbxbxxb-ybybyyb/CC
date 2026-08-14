from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_CorrMaxVolumeZScore_13h(BaseFactor):
    """
    *因子名 : HF_CorrMaxVolumeZScore_13h
    *因子功能描述 : 成交量与最高价的相关性，并取其ZScore；值越大，表示价量齐升，超买越多，收益越低
    *因子参数 :  MinuteHigh--分钟最高价,MinuteVolume--分钟成交量
    *作者 : hezq
    *因子创建日期 : 2019.7.2

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 60


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']  

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))[-1]
        # print(date_list)
        volume_today = MinuteVolume.loc[date_list].sort_index(ascending=True).rank(axis=0,method='first',ascending=True)
        high = MinuteHigh.loc[date_list].sort_index(ascending=True).rank(axis=0,method='first',ascending=True)
        res = Util.array_coef(volume_today,high)
        return res
        
    def reform(self, df):
        df = (df-df.rolling(window=self.reform_window,min_periods=1).mean())/df.rolling(window=self.reform_window,min_periods=1).std()
        df[np.isinf(df)] = np.nan
        return -df