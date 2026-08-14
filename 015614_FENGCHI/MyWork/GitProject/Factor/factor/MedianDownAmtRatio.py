import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class MedianDownAmtRatio(BaseFactor):
    # 因子名称：MedianDownAmtRatio
    # 计算公式：过去20天市场下跌时的平均成交额 / 过去20天平均成交额，截面中心化后取绝对值再取相反数，取20天平均
    # 因子逻辑：市场下跌时和上涨时的成交量越相近，该因子值越大，这样的股票噪音交易者和投机行为比例较少
    depend_data = ['FactorData.Basic_factor.close', 'FactorData.Basic_factor.amt',
                   'FactorData.Basic_factor.adjfactor']
    lag = 20
    reform_window = 20

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = close.columns
        close, amt, adj = close.values, amt.values, adj.values
        close = close * adj / adj[-1]
        r = close[1:] / close[:-1] - 1
        mkt_r = np.tile(np.nanmean(r, axis=1).reshape((len(r), 1)), (1, len(stk_code)))
        amt = amt[1:]
        res = np.nanmean(np.where(mkt_r < 0, amt, np.nan), axis=0) / np.nanmean(amt, axis=0)
        res = pd.Series(-np.abs(res - np.nanmean(res)), index=stk_code)
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(20).mean()
        return alpha
