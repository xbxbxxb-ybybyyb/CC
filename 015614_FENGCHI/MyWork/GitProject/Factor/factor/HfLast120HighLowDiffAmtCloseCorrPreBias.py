"""
    *因子名 : HfLast120HighLowDiffAmtCloseCorrPreBias
    *因子功能描述 : 开盘2小时高低价成交额之差与前1分钟收盘价的负相关系数的乖离值; 分钟高低价成交额差值变化与股价变化背离，说明上涨动能衰竭,乖离值越高，说明趋势越强
    *因子参数 : MinuteHigh-分钟最高价, MinuteLow-分钟最低价, MinuteClose-分钟收盘价, MinuteVolume-分钟成交量
    *作者 : 沈天琦(shentq)
    *因子创建日期 : 2019.07.22
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
"""

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj

class HfLast120HighLowDiffAmtCloseCorrPreBias(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute','FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute','FactorData.Basic_factor.volume_minute']    
    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 5
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        minute_high = MinuteHigh.iloc[-240:]
        minute_low = MinuteLow.iloc[-240:]
        minute_close = MinuteClose.iloc[-240:]
        minute_volume = MinuteVolume.iloc[-240:]

        minute_swing_diff_amt = (minute_high - minute_low) * minute_volume
        
        result = -Util.array_coef(minute_swing_diff_amt[-120:],minute_close.shift(1)[-120:])
        
        return result

    def reform(self, temp_result):
        return temp_result - temp_result.rolling(window=self.reform_window,min_periods=1).mean()

    # def __init__(self, json_path):
    #     super(HfLast120HighLowDiffAmtCloseCorrPreBias_13h, self).__init__(json_path)
        
    # def definition(self, MinuteHigh, MinuteLow, MinuteClose, MinuteVolume):

    #     factor_values = self.minute_help(self.minute, 'HfLast120HighLowDiffAmtCloseCorrPreBias_13hHelp', MinuteHigh, MinuteLow, MinuteClose, MinuteVolume)
    #     factor_values = factor_values - factor_values.rolling(window=5,min_periods=1).mean()
        
    #     return factor_values

    # def minute(self, MinuteHigh, MinuteLow, MinuteClose, MinuteVolume):
    #     fmt = '%Y-%m-%d'
        
    #     date_list = np.unique(MinuteHigh.index.strftime(fmt))

    #     last_date = date_list[-2]
    #     current_date = date_list[-1]

    #     df_factor = pd.DataFrame(index=[pd.Timestamp(current_date)], columns=MinuteHigh.columns)

    #     minute_high = MinuteHigh.loc[last_date].append(MinuteHigh.loc[current_date])[-240:]
    #     minute_low = MinuteLow.loc[last_date].append(MinuteLow.loc[current_date])[-240:]
    #     minute_close = MinuteClose.loc[last_date].append(MinuteClose.loc[current_date])[-240:]
    #     minute_volume = MinuteVolume.loc[last_date].append(MinuteVolume.loc[current_date])[-240:]

    #     minute_swing_diff_amt = (minute_high - minute_low) * minute_volume
        
    #     df_factor.loc[current_date] = -minute_swing_diff_amt[-120:].corrwith(minute_close.shift(1)[-120:])
        
    #     return df_factor