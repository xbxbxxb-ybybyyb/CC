import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class AmtPerDealRetCorr(BaseFactor):
    # 因子名称：AmtPerDealRetCorr
    # 计算公式：平均单笔成交金额与日收益率的相关系数
    # 因子逻辑：股价下跌时容易引发反应过度，此时单笔成交金额较大而收益率较小，股价后续可能反弹；股价上涨过程中通常会反应不足，此时单笔成交金额
    # 较小而收益率较大，股价后续会继续补涨
    depend_data = ['FactorData.Basic_factor.dealnum', 'FactorData.Basic_factor.volume',
                   'FactorData.Basic_factor.adjfactor', 'FactorData.Basic_factor.amt']
    lag = 20

    def calc_single(self, database):
        deal = database.depend_data['FactorData.Basic_factor.dealnum']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        stk_code = deal.columns
        p = amt.values / volume.values * adj.values / adj.values[-1]
        r = p[1:] / p[:-1] - 1
        amt, deal = amt.values[1:], deal.values[1:]
        amt_per_deal = amt / deal
        res = array_corr_np(r, amt_per_deal)
        res = pd.Series(-res, index=stk_code)
        return res
