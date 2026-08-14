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


class SellRtnSellMoneyDiffCorr(BaseFactor):
    # 因子名称：SellRtnSellMoneyDiffCorr
    # 计算公式：过去20天主动卖单成交均价的收益率与主动卖单成交金额的变动的相关系数，取相反数，再取5日平均
    # 因子逻辑：股价下跌时容易引发反应过度，此时卖单成交额增大而卖单成交均价收益率较低，股价后续可能反弹
    depend_data = ['FactorData.WIND_AShareL2Indicators', 'FactorData.Basic_factor.amt',
                   'FactorData.Basic_factor.close', 'FactorData.Basic_factor.adjfactor']
    financial_lag = 20
    reform_window = 5

    def calc_single(self, database):
        l2 = database.depend_data['FactorData.WIND_AShareL2Indicators']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = adj.columns
        sell_mon = l2['S_LI_INITIATIVESELLMONEY'].unstack().reindex(columns=stk_code).values[-20:]
        sell_amt = l2['S_LI_INITIATIVESELLAMOUNT'].unstack().reindex(columns=stk_code).values[-20:]
        sell_p = sell_mon / sell_amt
        sell_r = sell_p[1:] / sell_p[:-1] - 1
        sell_d_mon = sell_mon[1:] - sell_mon[:-1]
        res = pd.Series(-array_corr_np(sell_r, sell_d_mon), index=stk_code)
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(5).mean()
        return alpha
