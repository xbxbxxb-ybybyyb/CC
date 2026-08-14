from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time



class MinTTM(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute',
                    'FactorData.Basic_factor.amt_minute',]    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # fix_times = ["1500"]
    reform_window = 60
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute'].iloc[-30:,:]
        volume = database.depend_data['FactorData.Basic_factor.volume_minute'].iloc[-30:,:]

        volume = volume.replace(0.,np.nan)
        vol = volume.values
        am = amt.values
        top = (vol > np.nanpercentile(vol,80,axis=0))
        tail = (vol < np.nanpercentile(vol,20,axis=0))
        vwap_top = np.nansum(am*top,axis=0) / np.nansum(vol*top,axis=0)
        vwap_tail = np.nansum(am*tail,axis=0) / np.nansum(vol*tail,axis=0)
        vwap_top = pd.Series(vwap_top, index = volume.columns)
        vwap_tail = pd.Series(vwap_tail, index = volume.columns)
        ratio = vwap_tail / vwap_top
        return ratio
        
        
    def  reform(self, temp_result):
        A = temp_result.rolling(60,1).min()
        return A
        