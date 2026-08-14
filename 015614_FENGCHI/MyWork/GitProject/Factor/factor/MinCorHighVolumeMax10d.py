from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class MinCorHighVolumeMax10d(BaseFactor):
    
    '''
    *因子名：MinCorHighVolumeMax10d
    *因子功能描述：分钟最高价和成交量10日最大相关性
    *因子参数：[MinuteHigh]: 分钟最高价
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.4.16
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
        
    '''

    factor_type = "DAY"
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_high_min, s_volume_min]

    reform_window = 10

    # def __init__(self, json_path):

    #     super(MinCorHighVolumeMax10d, self).__init__(json_path)
        

    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        high_min = database.depend_data[self.s_high_min]
        volume_min = database.depend_data[self.s_volume_min]
        CorrVolumePrice = self.minute(high_min, volume_min)

        # CorHighVolumeMax = CorrVolumePrice.rolling(window=n,min_periods=int(0.8*n)).max()

        # return -CorHighVolumeMax
        return CorrVolumePrice
    
    def reform(self, temp_result):
        return -temp_result.rolling(self.reform_window, min_periods = int(.8 * self.reform_window)).max()

    def minute(self,MinuteHigh,MinuteVolume):
        
        high = MinuteHigh
        volume = MinuteVolume
        CorrVolumePrice = Util.array_coef(high, volume)

        CorrVolumePrice=CorrVolumePrice.convert_objects(convert_numeric=True)

        return CorrVolumePrice