from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VolumeMax10min2All_13h(BaseFactor):

    """
    *因子名：VolumeMax10min2All_13h
    *因子功能描述：当日截至13:00，10min最大成交量/今日和昨日10点前成交量之和
    该值越大，说明上涨时成交量越大且稳定，后市存在上涨动量。
    *因子参数：[MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.8.29
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        dates = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        compute_date = dates[-1]
        pre_date = dates[-2]
        volume = v.loc[compute_date]
        volumeMax = (volume.rolling(window=10,min_periods=10).sum()).max()
        volumeAll = volume.sum()
        volumeAll_pre = v.loc[pre_date].iloc[:120].sum()
        VolumeMax10min2All = volumeMax/(volumeAll+volumeAll_pre)
        
        return -VolumeMax10min2All