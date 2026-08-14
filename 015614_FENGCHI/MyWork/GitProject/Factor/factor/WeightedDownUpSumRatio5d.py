from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time



class WeightedDownUpSumRatio5d(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.open_minute', 'FactorData.Basic_factor.close_minute',
                    'FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag = 0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series


    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        _open = database.depend_data['FactorData.Basic_factor.open_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        # print(close.shape)


        _open = _open.iloc[210:]
        # print(_open.shape)
        # close = minute_close.loc[date][210:]
        close = close.iloc[210:]
        # volume = minute_volume.loc[date][210:]
        volume = volume.iloc[210:]
        
        diff = (close - _open) * volume
        diff_abs = np.abs(diff)
        diff_up = (diff_abs.values + diff.values) / 2.
        diff_up=pd.DataFrame(diff_up, index = diff.index, columns = diff.columns)
        diff_down = (diff_abs.values - diff.values) / 2.
        diff_down=pd.DataFrame(diff_down, index = diff.index, columns = diff.columns)

        
        up = diff_up.sum()
        down = diff_down.sum()
        
        ratio = down / up
        ratio[np.isinf(ratio)] = np.nan
        ratio[np.isnan(ratio)] = 0

        # _open = _open[210:]
        # close = close[210:]
        # volume = volume[210:]
        
        # diff = (close - _open) * volume
        # diff_abs = np.abs(diff)
        # diff_up = (diff_abs + diff) / 2
        # diff_down = (diff_abs - diff) / 2
        
        # up = diff_up.sum()
        # down = diff_down.sum()
        
        # ratio = down / up
        # ratio[np.isinf(ratio)] = np.nan
        # ratio[np.isnan(ratio)] = 0
            
        return ratio


    def  reform(self, temp_result):
        A = temp_result.rolling(5,1).mean()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A