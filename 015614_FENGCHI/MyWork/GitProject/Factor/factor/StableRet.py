from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj

# ["FactorDailyStableRet",{'n': 20, 'Data_Base': ['play_day_minute_close'], 'play_day_lag': 20,'play_min_lag': None,
#     'generator_lag': 1,'type': 1500}, "F_D_StableRet.h5"]

class StableRet(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 19
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data)
        minute_close = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_close = min_forward_adj(minute_close)
        ret_5min = np.log(minute_close) - np.log(minute_close.shift(-5))
        for i in range(int(ret_5min.shape[0] / 240)):
            ret_5min.iloc[i * 240 + 235:i * 240 + 240, :] = np.nan
        ret_5min = ret_5min.resample('5min', how='first')
        ret_5min = ret_5min.dropna(how='all')
        rvol = ret_5min.resample('1D').std()
        rvol = rvol.dropna(how='all')
        sdrvol = rvol.rolling(20).std() / rvol.rolling(20).mean()
        ans = sdrvol
        ans = ans.iloc[-1, :]
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。


