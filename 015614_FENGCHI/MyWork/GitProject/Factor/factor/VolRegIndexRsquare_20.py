from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as ut


class VolRegIndexRsquare_20(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume-000905.SH", "FactorData.Basic_factor.volume_by_share"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 42

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 20

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        stock_vol = database.depend_data["FactorData.Basic_factor.volume_by_share"]
        index_vol = database.depend_data['FactorData.Basic_factor.volume-000905.SH']
        temp_df = pd.concat([stock_vol, np.log(index_vol)], axis=1)
        factor_mean = temp_df.mean(axis=1)
        factor_std = temp_df.std(axis=1)
        value_df = temp_df.sub(factor_mean, axis=0)
        temp_df_zscore = value_df.div(factor_std, axis=0)
        index_vol_log = temp_df_zscore.iloc[:, -1]
        stock_vol_zscore = temp_df_zscore.iloc[:, :-1]

        stock_vol_log_i = stock_vol_zscore.iloc[-20:]
        stock_mkt_cap_log_i = index_vol_log.iloc[-20:]
        ff = np.vstack([np.array(stock_mkt_cap_log_i), np.ones(len(stock_mkt_cap_log_i))])
        reg = np.linalg.inv(ff.dot(ff.T)).dot(ff).dot(np.array(stock_vol_log_i))
        stock_res = stock_vol_log_i - ff.T.dot(reg)
        stock_vol_log_i_mean = stock_vol_log_i.mean(axis=0)
        temp_df = stock_vol_log_i.copy()
        for i in range(temp_df.shape[0]):
            temp_df.iloc[i, :] = stock_vol_log_i_mean
        stock_vol_log_i_sub = stock_vol_log_i - temp_df
        SST = np.square(stock_vol_log_i_sub).sum(axis=0)
        SSE = np.square(stock_res).sum(axis=0)
        R_Square = (SST - SSE) / SST
        ans = R_Square
        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    # def reform(self, temp_result):
    #     return temp_result.rolling(self.reform_window).std()

