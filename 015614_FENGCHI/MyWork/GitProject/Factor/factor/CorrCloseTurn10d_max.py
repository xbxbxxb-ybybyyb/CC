# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class CorrCloseTurn10d_max(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.turn"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 20

    def get_corr(self, factor1, factor2, n):
        cor = pd.DataFrame(index=factor1.index, columns=factor1.columns)
        sum_ = factor1 + factor2
        sum_valid_n = (~np.isnan(sum_)).rolling(window=n, min_periods=1).sum()
        for i in range(n - 1, factor1.shape[0]):
            cor.iloc[i] = array_corr_np(factor1.iloc[i - n + 1:i + 1].values, factor2.iloc[i - n + 1:i + 1].values)
        cor[sum_valid_n.values < (0.8 * n)] = np.nan
        return cor

    def calc_single(self, database):
        n = 10
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        corr = self.get_corr(close_adj, turn, n)
        corr = corr.astype(np.float64)
        corr_max = corr.rolling(window=n, min_periods=int(0.8 * n)).max()

        return -corr_max.iloc[-1, :]