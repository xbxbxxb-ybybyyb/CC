from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CloseVolumeCorrBias20d(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_adj_minute', 'FactorData.Basic_factor.close_adj_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 1
    minute_lag=1
    # fix_times = ["1300"]
    reform_window = 20

    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        MinuteVolume = MinuteVolume.iloc[240:,:].groupby(pd.Grouper(freq = '5min')).sum()
        # .dropna(how = 'all')
        MinuteClose = MinuteClose.iloc[240:,:].groupby(pd.Grouper(freq = '5min')).last()
        # .dropna(how = 'all')
        return Util.array_coef(MinuteClose, MinuteVolume)
        

    def  reform(self, factor):
        A = -(factor-factor.rolling(20).mean())/factor.rolling(20).std()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A
    