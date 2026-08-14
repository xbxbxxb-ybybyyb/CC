from xfactor.BaseFactor import BaseFactor
import xfactor.Util as ut
import numpy as np
import pandas as pd


class ExceedSwingCorAmt(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high", "FactorData.Basic_factor.low", "FactorData.Basic_factor.high-000905.SH",
                   "FactorData.Basic_factor.low-000905.SH", "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.amt_by_yuan", "FactorData.Basic_factor.mkt_cap_ard"]
    #依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 28
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        high = database.depend_data['FactorData.Basic_factor.high']
        low = database.depend_data['FactorData.Basic_factor.low']
        index_high = database.depend_data['FactorData.Basic_factor.high-000905.SH']
        index_high.columns = ['000905.SH']
        index_low = database.depend_data['FactorData.Basic_factor.low-000905.SH']
        index_low.columns = ['000905.SH']
        amt = database.depend_data["FactorData.Basic_factor.amt_by_yuan"]
        mkt = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        high_adj = high * adj
        low_adj = low * adj

        stock_swing = 2 * (high_adj - low_adj)/(high_adj + low_adj)
        index_swing = 2 * (index_high - index_low)/(index_high + index_low)
        # a = pd.Series(index_swing)
        exceed_swing = stock_swing.sub(index_swing['000905.SH'], axis=0)
        stock_amt = amt[amt > 0]
        df = ut.array_coef(exceed_swing.iloc[-25:], stock_amt.iloc[-25:])
        mkt = np.log(mkt).iloc[-1]
        temp_df = pd.concat([df, mkt], axis=1)
        temp_df.columns = ['a', 'b']
        temp_df.dropna(inplace=True)
        ff = np.vstack([np.array(temp_df['b']), np.ones(len(temp_df['b']))])
        reg = np.linalg.inv(ff.dot(ff.T)).dot(ff).dot(np.array(temp_df['a']))
        stock_res = temp_df['a'] - ff.T.dot(reg)

        return -stock_res

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    # def reform(self, temp_result):
    #     return temp_result.rolling(self.reform_window).mean()
