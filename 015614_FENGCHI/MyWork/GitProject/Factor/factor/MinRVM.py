from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time



class MinRVM(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.open_minute',
                'FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1500"]
    reform_window = 10
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        min_close = database.depend_data['FactorData.Basic_factor.close_minute']
        min_open = database.depend_data['FactorData.Basic_factor.open_minute']
        min_turn = database.depend_data['FactorData.Basic_factor.amt_minute']
        min_volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        min_return5 = min_close[4::5].values / min_open[0::5].values - 1
        

        min_turn5 = (min_turn.rolling(window=5, min_periods=1).sum())[4::5]
        min_volume5 = (min_volume.rolling(window=5, min_periods=1).sum())[4::5]
        min_RV5 = np.abs(min_return5) / min_volume5.values
        RV_flag = (min_RV5 >= np.nanpercentile(min_RV5,90,axis=0))
        vwap_RV5 = np.nansum(min_turn5.values * RV_flag, axis=0) / np.nansum(min_volume5.values * RV_flag, axis=0)
        vwap_allday = min_turn.sum() / min_volume.sum()
        df_ratio = vwap_RV5 / vwap_allday
        return df_ratio

     

    def  reform(self, temp_result):
        A = temp_result.rolling(10,1).mean()
        return A
        