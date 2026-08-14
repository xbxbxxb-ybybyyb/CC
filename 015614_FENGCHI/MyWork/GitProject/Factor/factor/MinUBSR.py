from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinUBSR(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.low_minute',
                'FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1500"]
    reform_window = 60
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        min_low = database.depend_data['FactorData.Basic_factor.low_minute']
        min_turn = database.depend_data['FactorData.Basic_factor.amt_minute']
        min_volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        min_volume = min_volume.replace(0.,np.nan)

        vwap = min_turn / min_volume
        price_ratio = (vwap-min_low)/min_low
        volume_rs = (vwap.diff().values>0)*min_volume.values
        vrs_flag1 = (volume_rs > np.nanpercentile(volume_rs,90,axis=0))
        v1 = vrs_flag1 * min_volume.values
        p1 = vrs_flag1 * price_ratio.values
        df_ratio = pd.DataFrame((v1*p1)/np.nansum(v1,axis=0), index=vwap.index, columns=vwap.columns).sum()
        return df_ratio




    def  reform(self, temp_result):
        A = temp_result.rolling(60,1).mean() / temp_result.rolling(60,1).std()
        return A
