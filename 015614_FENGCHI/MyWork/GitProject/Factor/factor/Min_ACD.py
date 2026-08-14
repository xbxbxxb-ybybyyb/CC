from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class Min_ACD(BaseFactor):
    """
    *因子名 : Min_ACD
    *因子功能描述 : 收盘价大于前收盘价时，用close-min(low,pre_close)衡量买入力量；收盘价小于前收盘价时，close-max(high,pre_close)衡量卖出力量，两者相加得到净买入力量。
    *因子参数 : MinuteHigh-分钟最高价,MinuteLow-分钟最低价,MinuteClose-分钟收盘价,Minute_Status-股票分钟状态,is_valid_raw-股票未上市、停牌、退市标志
    *作者 : hezq
    *因子创建日期 : 2019.1.3
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改

    """
    factor_type = "DAY"
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_low_min = 'FactorData.Basic_factor.low_minute'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    depend_data = [s_high_min, s_low_min, s_close_min]

    reform_window = 5
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        high_min = database.depend_data[self.s_high_min]
        low_min = database.depend_data[self.s_low_min]
        close_min = database.depend_data[self.s_close_min]
        up_var = self.minute(high_min, low_min, close_min)
        return up_var

    # def definition(self,MinuteHigh,MinuteLow,MinuteClose,Minute_Status,is_valid_raw):
    #     up_var = self.minute_help(self.minute,'ACDHelp',MinuteHigh,MinuteLow,MinuteClose)
    #     up_var = -up_var[(Minute_Status==0)|(Minute_Status==2)|(Minute_Status==4)]
    #     up_var = up_var.rolling(window=5,min_periods=1).mean()
    #     up_var = up_var[is_valid_raw==1]
        
    #     return up_var
    
    def reform(self, temp_result):
        f = -temp_result
        return f.rolling(self.reform_window, 1).mean()

    
    def minute(self,MinuteHigh,MinuteLow,MinuteClose): 
        high = MinuteHigh
        code ,min_date = high.columns, high.index
        close = MinuteClose
        low = MinuteLow
        accu = pd.DataFrame(close.diff(axis=0).values > 0, index=high.index, columns=high.columns)
        dist = pd.DataFrame(close.diff(axis=0).values <= 0, index=high.index, columns=high.columns)

        min_low_close = np.where(close.shift(1)>low,low,close.shift(1))
        min_low_close = pd.DataFrame(min_low_close,index=min_date,columns=code)[accu]# 筛出收集力量
        min_low_close = (close-min_low_close).sum(axis = 0)
        min_low_close = min_low_close[accu.sum(axis=0) != 0]## 剔除全为0的无效股票

        max_high_close = np.where(close.shift(1)>high,close.shift(1),high)
        max_high_close = pd.DataFrame(max_high_close,index=min_date,columns=code)[dist]
        max_high_close = (close-max_high_close).sum(axis=0)
        max_high_close = max_high_close[dist.sum(axis=0)!=0]

        res = min_low_close + max_high_close
        return res