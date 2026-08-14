from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class Min_PredictReturn2Volume(BaseFactor):
    """
    *因子名 : Min_PredictReturn2Volume
    *因子功能描述 :收盘前30分钟，利用收益率乘上成交量的增长，表示放量涨还是放量跌的状态
    *因子参数 :  MinuteClose-分钟收盘价，MinuteVolume-分钟交易量,Minute_Status-股票分钟状态
    *作者 : hezq
    *因子创建日期 : 2019.04.17
    """
    factor_type = "DAY"
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_close_min, s_volume_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        volume_min = database.depend_data[self.s_volume_min]
        return self.minute(close_min, volume_min)

    # def definition(self,MinuteClose,MinuteVolume,Minute_Status):
    #     # up_var = self.minute_help(self, ,'testHelp',MinuteClose,MinuteVolume)
    #     up_var = up_var[(Minute_Status==0)]
    #     return up_var

    def minute(self,MinuteClose,MinuteVolume): 
        Close = MinuteClose
        Volume = MinuteVolume
        res = (Volume/(Volume.shift(1)))* (Close/Close.shift(1)-1)
        res[np.isinf(res)]=np.nan
        res = res.iloc[-30:,:].sum(axis=0)
        res[Volume.iloc[-30:,:].sum(axis=0)==0]=np.nan
        return -res