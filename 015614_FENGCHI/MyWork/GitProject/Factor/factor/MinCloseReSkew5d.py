from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinCloseReSkew5d(BaseFactor):
    
    '''
    *因子名：MinCloseReSkew5d
    *因子功能描述：收盘价相对任意分钟收盘价收益率的偏度的5日均值
    *因子参数：[MinuteClose]: 分钟收盘价
               [n]: 回看天数

    *作者：周璇
    *因子创建日期：2019.6.3
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
        
    '''
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_minute']
        def skewness(data):
            var = np.nansum(data**2)
            sum3 = np.nansum(data**3)
            skew = np.sqrt(np.where(~np.isnan(data))[0].shape[0])*sum3/(var**1.5)
            return skew
        r = 1 - c.values / c.values[-1]
        ms = np.apply_along_axis(skewness, 0, r)
        ms = pd.Series(index=c.columns, data=ms).convert_objects(convert_numeric=True)
        return ms

    def reform(self, temp):
        MinCloseReSkew5d = temp.rolling(window=self.reform_window, min_periods=int(self.reform_window*0.8)).mean()
        return -MinCloseReSkew5d