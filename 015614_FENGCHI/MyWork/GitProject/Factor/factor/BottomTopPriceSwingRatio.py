from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class BottomTopPriceSwingRatio(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute',
                    'FactorData.Basic_factor.adjfactor']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 2
    minute_lag=1
    # fix_times = ["1300"]
    # reform_window = 20

    
    def calc_single(self, database):

        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
    
        t1 = time.time()
        m = MinuteVolume.iloc[120:240]
        adj1 = self.S2D(adjfactor.iloc[1,:], m)
        adj0 = self.S2D(adjfactor.iloc[0,:], m)
        MinuteVolume = (MinuteVolume.iloc[120:240] * adj1 / adj0).append(MinuteVolume.iloc[240:])
        MinuteTurnover = MinuteTurnover.iloc[120:]
        v = MinuteTurnover.astype(np.float64) / MinuteVolume.astype(np.float64)
        vwap = v.rolling(10)
        mean = vwap.mean()
        swing = vwap.max() - vwap.min()
        f1 = pd.DataFrame((mean.values == np.tile(mean.min().values,(v.shape[0],1))), index=v.index, columns=v.columns)
        f2 = pd.DataFrame((mean.values == np.tile(mean.max().values,(v.shape[0],1))), index=v.index, columns=v.columns)
        alpha = swing[f1].mean() /  swing[f2].mean()
        alpha[np.isinf(alpha.values)] = np.nan
        return alpha


    def S2D(self, S, D):
        return pd.DataFrame(np.tile(S.values,(D.shape[0],1)),index=D.index,columns=D.columns)