from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class HF_AmtDeg1(BaseFactor):
    """
    *因子名 : HF_AmtDeg1_13h
    *因子功能描述 : 以开盘价计算的成价额对收盘价的回归系数，表示过去的成交量对价格的影响，值越大越超买，收益越低
    *因子参数 : MinuteClose-分钟收盘价，MinuteOpen-分钟开盘价，MinuteVolume-分钟成交量
    *作者 : hezq
    *因子创建日期 : 2019.7.23

    """
    factor_type = 'FIX'
    s_open_min = 'FactorData.Basic_factor.open_minute'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_open_min, s_close_min, s_volume_min]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        open_min = database.depend_data[self.s_open_min]
        close_min = database.depend_data[self.s_close_min]
        volume_min = database.depend_data[self.s_volume_min]
        df = self.minute(open_min, close_min, volume_min)
        return -df

    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        return temp_result

    def minute(self,MinuteOpen,MinuteClose,MinuteVolume): 
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        volume_today = MinuteVolume.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        open_ = MinuteOpen.sort_index(ascending=True)
        amt = volume_today*open_
        res = Util.array_coef(amt, close)*close.std(axis=0)/amt.std(axis=0)
        return res