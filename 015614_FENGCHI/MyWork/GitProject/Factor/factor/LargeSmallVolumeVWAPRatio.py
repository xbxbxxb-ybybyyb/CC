from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np


class LargeSmallVolumeVWAPRatio(BaseFactor):
    """
    * LargeSmallVolumeVWAPRatio
    * 因子功能描述：今日大小交易量的VWAP二阶导标准差之差,大小交易量定义为0.8和0.2百分位
    * 因子参数：MinuteTurnover, MinuteVolume
    * 作者：孔剑阳
    * 因子创建日期： 2019.09.30
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "DAY"
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_amt_min, s_volume_min]
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt_min = database.depend_data[self.s_amt_min]
        volume_min = database.depend_data[self.s_volume_min]
        return self.minute(amt_min, volume_min)


    def minute(self, MinuteTurnover, MinuteVolume):
        PriceDiff = (MinuteTurnover/MinuteVolume).pct_change(5)
        Volume_large = MinuteVolume >= MinuteVolume.quantile(0.9)
        Volume_small = MinuteVolume <= MinuteVolume.quantile(0.1)
        SmallDiff = (Volume_small * PriceDiff.diff(5)).std() 
        LargeDiff = (Volume_large * PriceDiff.diff(5)).std() 
        f = SmallDiff - LargeDiff
        return  f

    # def definition(self, MinuteTurnover, MinuteVolume):
    #     df_single_day = self.minute_help(self.minute, 'LargeSmallVolumeVWAPRatio', MinuteTurnover, MinuteVolume)
    #     return df_single_day