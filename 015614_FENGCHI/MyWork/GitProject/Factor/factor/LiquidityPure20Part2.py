from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd


class LiquidityPure20Part2(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.mkt_cap_ard"]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 19
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        amt = database.depend_data['FactorData.Basic_factor.amt_minute'].copy()
        mkt_cap = database.depend_data['FactorData.Basic_factor.mkt_cap_ard'].copy()
        mkt_cap.index = pd.to_datetime([pd.datetime.strptime(item, '%Y%m%d') for item in mkt_cap.index])
        mkt_cap_min = mkt_cap.resample('1min', how='first')
        mkt_cap_min = mkt_cap_min.fillna(method='ffill')
        mkt_cap_min = mkt_cap_min.reindex(amt.index)
        mkt_cap_min.iloc[-1, :] = np.array(mkt_cap.iloc[-1, :])
        mkt_cap_min = mkt_cap_min.fillna(method='bfill')
        turn_min = amt / mkt_cap_min
        turn_sum_ln = np.log(turn_min.sum(axis=0, skipna=True))
        turn_sum_ln[np.isinf(turn_sum_ln)] = np.nan
        liq_daily = self.get_res(turn_sum_ln, np.log(mkt_cap.iloc[-1, :].astype('float')))
        liq_daily = liq_daily.reindex(amt.columns)
        index_filter = np.concatenate([np.arange(i * 242 + 61, i * 242 + 121, 1) for i in range(int(turn_min.shape[0] / 242))])
        turn_min_part_sum_ln = np.log(turn_min.iloc[index_filter, :].sum(axis=0))
        turn_min_part_sum_ln[np.isinf(turn_min_part_sum_ln)] = np.nan
        liq_sub = self.get_res(turn_min_part_sum_ln, mkt_cap.iloc[-1, :])
        liq_sub = liq_sub.reindex(amt.columns)
        liq_pure = self.get_res(liq_sub, liq_daily)
        liq_pure = liq_pure.reindex(amt.columns)
        ans = liq_pure
        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。

    def get_res(self, y: pd.Series, x: pd.Series, intersect=True):
        y_isnan = np.isnan(y.astype('float'))
        x_isnan = np.isnan(x.astype('float'))
        y_isvalid = 1 - y_isnan
        x_isvalid = 1 - x_isnan
        valids = x_isvalid * y_isvalid
        y_valid = y[valids == 1]
        x_valid = x[valids == 1]
        if intersect:
            x_valid = np.array([np.ones(x_valid.shape),x_valid]).T
            b = np.linalg.inv((x_valid.T.dot(x_valid)).astype('float')).dot(x_valid.T).dot(y_valid)
            residual = y_valid - x_valid.dot(b)
        else:
            x_valid = x_valid.T
            b = x_valid.T.dot(y_valid)/(x_valid.T.dot(x_valid))
            residual = y_valid - x_valid * b
        return residual

