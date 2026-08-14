from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
from xfactor.FixUtil import minute_data_transform

class DownUpSumRatio5d(BaseFactor):
    """
    *因子名 : DownUpSumRatio5d
    *因子功能描述 : 全天分钟价格累计降低值，全天分钟价格累计上升值，求两者之比；取五日平均。

    *因子参数 : minute_open -- 分钟开盘价, minute_close -- 分钟收盘价
    *作者 : 徐志鑫
    *因子创建日期 : 2019.01.16
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
    """
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.close_minute"]    
    lag = 0  
    reform_window = 5
    
    def calc_single(self,database): 
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        minute_open = database.depend_data['FactorData.Basic_factor.open_minute']
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        dates = np.unique(minute_open.index.strftime(fmt))
        df_result = pd.DataFrame(index=[pd.Timestamp(date) for date in dates],columns=minute_open.columns)

        for date in dates:
            _open = minute_open.loc[date]
            close = minute_close.loc[date]
            
            diff = close - _open
            diff_abs = np.abs(diff)
            diff_up = (diff_abs + diff) / 2
            diff_down = (diff_abs - diff) / 2
            
            up = diff_up.sum()
            down = diff_down.sum()
            
            ratio = down / up
            ratio[np.isinf(ratio)] = np.nan
            ratio[np.isnan(ratio)] = 0
            
            df_result.loc[date] = ratio            
        return df_result.iloc[-1,:]
        
    def reform(self, temp_result):
        # 计算n日波动率
        alpha = temp_result.rolling(window=self.reform_window,min_periods=1).mean()
        return alpha
