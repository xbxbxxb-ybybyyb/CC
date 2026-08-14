from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class TurnWeiRet5min(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.free_float_shares","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=5
    factype='min'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'],limit_status,method='minute')
        share = database.depend_data['FactorData.Basic_factor.free_float_shares']
        ret = pd.DataFrame(np.log(close.values/close.shift(1).values), index=close.index, columns=close.columns)
        turn = volume.values / share.values
        weighted_ret = pd.DataFrame((turn * ret).values / turn.sum(axis=0), index=ret.index, columns=ret.columns)
        ans = weighted_ret.sum(axis=0)
        return ans

    def reform(self, temp_result):
        ans = temp_result
        if self.factype == 'mean':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window/2)).mean()
        elif self.factype == 'std':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window/2)).std()
        elif self.factype == 'min':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window / 2)).min()
        elif self.factype == 'max':
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window / 2)).max()
        elif self.factype == 'delta':
            alpha = ans - ans.shift(self.reform_window)
        elif self.factype == 'slope':
            def get_slope(x: pd.Series):
                def get_beta(y: pd.Series, x: pd.Series, intersect=True):
                    y_isnan = np.isnan(y)
                    x_isnan = np.isnan(x)
                    y_isvalid = 1 - y_isnan
                    x_isvalid = 1 - x_isnan
                    valids = x_isvalid * y_isvalid
                    y_valid = y[valids == 1]
                    x_valid = x[valids == 1]
                    if intersect:
                        x_valid = np.array([np.ones(x_valid.shape), x_valid]).T
                        if np.linalg.det(x_valid.T.dot(x_valid)) == 0:
                            beta = [np.nan, np.nan]
                        else:
                            b = np.linalg.inv(x_valid.T.dot(x_valid)).dot(x_valid.T).dot(y_valid)
                            beta = b
                    else:
                        x_valid = x_valid.T
                        b = x_valid.T.dot(y_valid) / (x_valid.T.dot(x_valid))
                        beta = b
                    return beta

                seq = pd.Series(np.arange(0, x.__len__(), 1)) + 1
                ans = get_beta(x, seq, intersect=True)[1]
                return ans
            alpha = ans.rolling(self.reform_window, min_periods=int(self.reform_window / 2)).apply(get_slope)
        return alpha


