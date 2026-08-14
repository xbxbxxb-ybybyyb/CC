from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform, min_forward_adj



class StaVolDivRetUpdown(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 19
    m = 20


# 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1


    @staticmethod
    def z_score_standardizer(value_df):
        factor_mean = value_df.mean()
        factor_std = value_df.std()
        value_df = value_df - factor_mean
        value_df = value_df / factor_std
        return value_df

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data)
        minute_volume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        vol_5min = minute_volume.resample('5min').sum()
        vol_5min[vol_5min.values == 0] = np.nan
        vol_5min = vol_5min.dropna(how='all')
        for i in range(int(vol_5min.shape[0] / 48)):
            vol_5min.iloc[i * 48, :] = np.nan
        vol_5min = vol_5min.dropna(how='all')
        vol_std = vol_5min.resample('1D').std()
        vol_std = vol_std.dropna(how='all')
        ans = vol_std.rolling(20).std() / vol_std.rolling(20).mean()
        ans = ans.iloc[-1, :]
        ans = self.z_score_standardizer(ans)

        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_close = min_forward_adj(minute_close)
        minute_ret = minute_close.pct_change(periods=1)
        minute_ret_cs = minute_ret.iloc[-self.m:]
        ret_cs_up = minute_ret_cs[minute_ret_cs > 0].sum()
        ret_cs_down = -minute_ret_cs[minute_ret_cs < 0].sum()
        ret_up_down = -ret_cs_up / ret_cs_down
        ret_up_down = self.z_score_standardizer(ret_up_down)

        ans1 = -0.1 / (ans + ret_up_down)
        return ans1

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。


