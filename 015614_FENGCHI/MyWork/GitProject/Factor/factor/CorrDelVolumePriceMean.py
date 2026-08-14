from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CorrDelVolumePriceMean(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=4
    # fix_times = ["1300"]
    # reform_window = 5

    
    def calc_single(self, database):



        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        # print(len(date_list))
        CorrDelVolumePrice = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list],columns=MinuteClose.columns)
        for date in date_list:
            close = MinuteClose.loc[date]
            volume = MinuteVolume.loc[date]
            v_change = (volume.diff(1)).abs()
            CorrDelVolumePrice.loc[date] = Util.array_coef(close, v_change)
        return -CorrDelVolumePrice.mean(axis=0)