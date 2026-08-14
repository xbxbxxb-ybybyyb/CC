from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class EWMSwing(BaseFactor):
    """
    *因子名 : EWMSwing_13h
    *因子功能描述 : 开盘到上午收盘，计算分钟振幅率的指数加权移动平均值，取最后一分钟的值。值越小，表示分钟波动越小，获取超额概率越大。

    *因子参数 : MinuteLow -- 分钟最低价, MinuteHigh -- 分钟最高价
    *作者 : 徐志鑫
    *因子创建日期 : 2019.08.07
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
    """
    factor_type = "FIX"
    s_low_min = 'FactorData.Basic_factor.low_minute'
    s_high_min = 'FactorData.Basic_factor.high_minute'
    depend_data = [s_low_min, s_high_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        low_min = database.depend_data[self.s_low_min]
        high_min = database.depend_data[self.s_high_min]
        return self.minute(low_min, high_min)

    def minute(self, MinuteLow, MinuteHigh):
        fmt = '%Y-%m-%d'
        dates = sorted(np.unique(MinuteLow.index.strftime(fmt)))

        today = dates[-1]

        low = MinuteLow.loc[today]
        high = MinuteHigh.loc[today]
        
        swing = (high - low) / low 
        ewm_swing = swing.ewm(alpha=0.95).mean()
        result = -ewm_swing.iloc[-1]
        
        return result
        
        
        
        

