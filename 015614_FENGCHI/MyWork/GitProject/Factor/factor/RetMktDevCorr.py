import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


def array_corr_np(x, y):
    y = np.tile(y.reshape((len(y), 1)), (1, x.shape[1]))
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class RetMktDevCorr(BaseFactor):
    # 因子名称：RetMktDevCorr
    # 计算公式：过去60天股票收益率与全市场股票收益率截面离散度的相关系数，取相反数
    # 因子逻辑：知情交易者可能会在市场分化不明显时去埋伏自己看好的股票，因此市场分化不明显时收益率相对较高的股票可能存在超额收益
    depend_data = ['FactorData.Basic_factor.close', 'FactorData.Basic_factor.adjfactor']
    lag = 60

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = close.columns
        close, adj = close.values, adj.values
        close = close * adj / adj[-1]
        r = close[1:] / close[:-1] - 1
        mkt_dev = np.nanstd(r, axis=1)
        res = pd.Series(-array_corr_np(r, mkt_dev), index=stk_code)
        return res
