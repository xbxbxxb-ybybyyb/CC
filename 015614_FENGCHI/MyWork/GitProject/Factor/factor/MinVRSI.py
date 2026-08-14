from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time


class MinVRSI(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute',
                    ]    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        volume = volume.replace(0.,np.nan)

        n = 6
        volume_5min = volume.groupby(pd.Grouper(freq='5min')).sum()
        volume_diff = volume_5min - volume_5min.shift()

        pos_diff = pd.DataFrame(volume_diff.values * (volume_diff.values > 0), index=volume_diff.index, columns=volume_diff.columns)
        ratio = pos_diff.iloc[-n:,:].sum() / volume_diff.abs().iloc[-n:,:].sum()

        return ratio



    def  reform(self, temp_result):
        A = temp_result.rolling(5,1).mean()
        return -A