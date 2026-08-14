from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class DownUpMeanRatio5d(BaseFactor):
    """
    *因子名 : DownUpMeanRatio5d
    *因子功能描述 : 下午阶段，分钟价格平均降低值，分钟价格平均上升值，求两者之比；取五日平均。

    *因子参数 : minute_open -- 分钟开盘价, minute_close -- 分钟收盘价
    *作者 : 徐志鑫
    *因子创建日期 : 2019.01.16
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 : 尚未修改
    """
    factor_type = "DAY"
    # fix_times = ["1500"]
    s_open_min = 'FactorData.Basic_factor.open_minute'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    depend_data = [s_open_min, s_close_min]
    reform_window = 5
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        open_min = database.depend_data[self.s_open_min]
        close_min = database.depend_data[self.s_close_min]
        return self.calc_ratio(open_min, close_min)

    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        temp_result[np.isnan(temp_result)] = 0
        return temp_result.rolling(self.reform_window, 1).mean()
    
    def calc_ratio(self, minute_open, minute_close): 

        _open = minute_open[120:]
        close = minute_close[120:]
        
        diff = close - _open
        diff_abs = np.abs(diff)
        diff_up = (diff_abs + diff) / 2
        diff_up[pd.DataFrame(diff_up.values==0, index=diff_up.index, columns=diff_up.columns)] = np.nan
        diff_down = (diff_abs - diff) / 2
        diff_down[pd.DataFrame(diff_down.values == 0, index=diff_down.index, columns=diff_down.columns)] = np.nan
        
        up = diff_up.mean()
        down = diff_down.mean()
        
        ratio = down / up
        # ratio[np.isinf(ratio)] = np.nan
        # ratio[np.isnan(ratio)] = 0
        
        # df_result.loc[date] = ratio
        
        return ratio

