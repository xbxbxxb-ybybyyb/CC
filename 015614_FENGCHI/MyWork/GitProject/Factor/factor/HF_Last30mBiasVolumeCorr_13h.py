# coding: utf-8

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_Last30mBiasVolumeCorr_13h(BaseFactor):

    """
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_adj_minute", "FactorData.Basic_factor.close_adj_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window = 0

    """ 
    """
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        
        close = MinuteClose.loc[pre_date].iloc[210:,:]
        volume = MinuteVolume.loc[pre_date].iloc[210:,:] 
        bias = (close - close.rolling(window=5).mean()) / close.rolling(window=5).mean()     
        corr = Util.array_coef(bias,volume)
        corr.fillna(0.0,inplace=True)
        return -corr
