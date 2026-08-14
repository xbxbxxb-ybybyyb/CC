from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time



class MinSCS(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.high_minute',
                    'FactorData.Basic_factor.open_minute',
                    'FactorData.Basic_factor.close_minute',
                    'FactorData.Basic_factor.amt_minute',
                    'FactorData.Basic_factor.low_minute',]    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        _open = database.depend_data['FactorData.Basic_factor.open_minute']
        amt = amt.replace(0.,np.nan)

        dt = 30
        shortcut = (high-low) + (high-low) - (_open-close).abs()
        illiq = shortcut / amt
        ratio = illiq.iloc[-dt:,:].sum(axis=0)
        return 1e6 * ratio
        
        
    def  reform(self, temp_result):
        A = temp_result.rolling(5,1).std()
        return A