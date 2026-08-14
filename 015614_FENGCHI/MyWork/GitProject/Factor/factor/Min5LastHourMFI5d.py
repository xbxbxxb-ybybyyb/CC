# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import sys
import time
import multiprocessing

class Min5LastHourMFI5d(BaseFactor):
    """

    *因子名 : Min5LastHourMFI5d
    *因子功能描述 : 五分钟数据最后一小时的MFI指标, rolling 5天的均值作为因子
                     
    *因子参数 : MinuteClose-分钟收盘价, MinuteHigh-分钟最高价, MinuteLow-分钟最低价, 
            MinuteVolume-分钟成交量, Minute_Status-分钟合法状态值, is_valid_raw-当天数据是否合法
    *作者 : wulb
    *因子创建日期 : 2019.4.16
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """
    factor_type = "DAY"
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_low_min = 'FactorData.Basic_factor.low_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_close_min, s_high_min, s_low_min, s_volume_min]

    reform_window = 5

    def calc_single(self, database):
        # status = (is_valid_raw == 0)|(Minute_Status == 1)|(Minute_Status == 2)|(Minute_Status == 3)|(Minute_Status == 5)
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_min = database.depend_data[self.s_close_min]
        high_min = database.depend_data[self.s_high_min]
        low_min = database.depend_data[self.s_low_min]
        volume_min = database.depend_data[self.s_volume_min]

        minute_factor_df = self.minute(close_min, close_min, low_min, volume_min)
        
        # minute_factor_df = -1 * minute_factor_df.rolling(window=5).mean()
        # minute_factor_df[is_valid_raw == 0] = np.nan
                
        return minute_factor_df

    def reform(self, temp_result):
        return - temp_result.rolling(self.reform_window).mean()
        
    def minute(self, MinuteClose, MinuteHigh, MinuteLow, MinuteVolume):
        # timestamp = MinuteClose.index[-1]
        close_5min = MinuteClose.asfreq(freq='5min').dropna(how='all')
        high_5min = MinuteHigh.asfreq(freq='5min').dropna(how='all')
        low_5min = MinuteLow.asfreq(freq='5min').dropna(how='all')
        volume_5min = MinuteVolume.groupby(pd.Grouper(freq='5min')).sum().dropna(how ='all')

        true_price = (close_5min + high_5min + low_5min) / 3
        true_price_shift = true_price.shift(1)

        temp = true_price * volume_5min

        temp1 = temp.where(true_price > true_price_shift, other=0)
        temp2 = temp.where(true_price < true_price_shift, other=0)

        v = temp1.rolling(window=6).mean() / temp2.rolling(window=6).mean()

        v2 = 100 - (100 / (1 + v))
        day_factor = v2.iloc[-1]

        # invalid_stock = status.columns[status.loc[cur_date]]
        # day_factor[invalid_stock] = np.nan      

        # factor_result[cur_date] = day_factor
        return day_factor        
    
        
    
            