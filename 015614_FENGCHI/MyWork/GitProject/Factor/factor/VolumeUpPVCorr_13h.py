from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform



class VolumeUpPVCorr_13h(BaseFactor):
    """
    *因子名 : VolumeUpPVCorr_13h
    *因子功能描述 : 上午最后一小时，分钟成交量高于上一分钟的时间段内，价格与成交量相关性。相关性越低超额越大。

    *因子参数 : MinuteVolume -- 分钟成交量, MinuteTurnover -- 分钟成交额, MinuteOpen -- 分钟开盘价, MinuteClose -- 分钟收盘价
    *作者 : 徐志鑫
    *因子创建日期 : 2019.07.24
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
    """

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.open_minute"]
    lag = 0
    minute_lag = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        o = database.depend_data['FactorData.Basic_factor.open_minute']
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        # dates = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        
        _open = o.iloc[-60:]
        close = c.iloc[-60:]
        volume = v.iloc[-60:]
        turnover = a.iloc[-60:]
        
        price = turnover / volume

        volume_diff = volume - volume.shift(1)
        volume_diff[volume_diff >= np.zeros(volume.shape)] = 1
        volume_diff[volume_diff < np.zeros(volume.shape)] = -1
        
        price_up = volume_diff[volume_diff >= np.zeros(volume.shape)] * price
        volume_up = volume_diff[volume_diff >= np.zeros(volume.shape)] * volume
        
        corr = Util.array_coef(price_up, volume_up)
        
        return -corr