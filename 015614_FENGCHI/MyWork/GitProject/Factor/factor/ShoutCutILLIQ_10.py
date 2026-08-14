from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd


class ShoutCutILLIQ_10(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.open", "FactorData.Basic_factor.close",
                   "FactorData.Basic_factor.high", "FactorData.Basic_factor.low",
                   "FactorData.Basic_factor.amt", "FactorData.Basic_factor.adjfactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 9

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        open_ = database.depend_data['FactorData.Basic_factor.open'] * adjfactor
        close = database.depend_data['FactorData.Basic_factor.close'] * adjfactor
        high = database.depend_data['FactorData.Basic_factor.high'] * adjfactor
        low = database.depend_data['FactorData.Basic_factor.low'] * adjfactor
        amt = database.depend_data['FactorData.Basic_factor.amt']
        short_cut = 2 * (high - low) - np.abs(open_ - close)
        df_temp = short_cut / amt
        ans = Util.rolling_process(df_temp, 'mean', self.lag+1)
        ans[ans == 0] = np.nan
        ans = ans.iloc[-1,:]
        return ans
