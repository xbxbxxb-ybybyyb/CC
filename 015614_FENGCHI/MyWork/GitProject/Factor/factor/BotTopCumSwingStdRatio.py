from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class BotTopCumSwingStdRatio(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute',
                    'FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1300"]
    # reform_window = 20

    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']


        high = MinuteHigh.rolling(len(MinuteHigh), min_periods=1).max()  # 累计最高价
        low = MinuteLow.rolling(len(MinuteLow), min_periods=1).min()  # 累计最低价
        ran = high - low  # 累计振幅
        thr_h, thr_l = high.values - ran.values * 0.2, low.values + ran.values * 0.2
        # r = (MinuteTurnover / MinuteVolume).pct_change()
        vwap = (MinuteTurnover / MinuteVolume)
        r = vwap.diff()/vwap.shift()
        # r = vwap.pct_change()
        f1 = pd.DataFrame((MinuteLow.values < thr_l), index = r.index, columns = r.columns)
        f2 = pd.DataFrame((MinuteHigh.values > thr_h), index = r.index, columns = r.columns)
        return r[f1].std() / r[f2].std()  # 振幅底端20%的收益率标准差 / 振幅顶端20%的收益率标准差