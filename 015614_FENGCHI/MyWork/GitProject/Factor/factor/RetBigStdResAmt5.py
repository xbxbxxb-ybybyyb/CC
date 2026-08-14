from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import pandas as pd

class RetBigStdResAmt5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=5
    reform_window=1
    period=5
    threshold=0.9
    pure=True

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        def get_res(y: pd.Series, x: pd.Series, intersect=True):
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
                    residual = pd.Series(np.zeros(y.shape) * np.nan, index=y.index)
                else:
                    b = np.linalg.inv(x_valid.T.dot(x_valid)).dot(x_valid.T).dot(y_valid)
                    residual = y_valid - x_valid.dot(b)
                    residual = residual.reindex(y.index)
            else:
                x_valid = x_valid.T
                if np.linalg.det(x_valid.T.dot(x_valid)) == 0:
                    residual = pd.Series(np.zeros(y.shape) * np.nan, index=y.index)
                else:
                    b = x_valid.T.dot(y_valid) / (x_valid.T.dot(x_valid))
                    residual = y_valid - x_valid * b
                    residual = residual.reindex(y.index)
            return residual
        period = str(self.period) + 'min'
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close =min_forward_adj(close)
        close = close.iloc[-237*(self.lag):, :].copy()
        volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].iloc[-237*(self.lag):, :].copy(),limit_status,method='minute')
        amt = data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'].iloc[-237*(self.lag):, :].copy(),limit_status,method='minute')
        ret = pd.DataFrame(np.log(close.values/close.shift(1).values),index=close.index,columns=close.columns)
        index = close.resample(period,how='last').dropna(how='all').index
        ret_min = ret.resample(period).sum().reindex(index)
        volume_min = volume.resample(period).sum().reindex(index)
        amt_min = amt.resample(period).sum().reindex(index)
        threshold = volume_min.quantile(self.threshold, axis=0)
        filter = np.zeros(volume_min.shape)
        filter[volume_min.values - threshold.values > 0] = 1
        ret_min_std = (ret_min * filter / filter).std()
        amt_min_std = (amt_min * filter / filter).std()
        if self.pure:
            ans = get_res(ret_min_std, amt_min_std)
        else:
            ans = ret_min_std
        return ans

    def reform(self, temp_result):
        alpha = temp_result
        return alpha


