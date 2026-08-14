from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np


def array_cov_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    return cov


class AgainstBeta(BaseFactor):
    """

    *因子名 : AgainstBeta
    *因子功能描述 : 计算非beta因子，即股票与市场beta之间的相关程度
    *因子参数 : close_adj-收盘价 open_adj-开盘价 is_valid-是否合法
    *函数返回值 : 非beta因子
    *作者 : 孙海平
    *因子创建日期 : 2019.2.19
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """        
    factor_type = "DAY"
    s_open = 'FactorData.Basic_factor.open'
    s_close = 'FactorData.Basic_factor.close'
    s_open_000001SH = 'FactorData.Basic_factor.open-000001.SH'
    s_close_000001SH = 'FactorData.Basic_factor.close-000001.SH'
    depend_data = [s_open, s_close, s_open_000001SH, s_close_000001SH]
    lag = 40
    reform_window = 40

    """
    股票与市场beta之间的相关程度
    """
    def calc_single(self, database):
        op = database.depend_data[self.s_open]
        close = database.depend_data[self.s_close]
        ret = close.values / op.values - 1
        open_market = database.depend_data[self.s_open_000001SH]
        close_market = database.depend_data[self.s_close_000001SH]
        columns = op.columns
        index = op.index
        ret_market = (close_market.values - open_market.values) / open_market.values
        ret_market = ret_market.reshape((len(index), 1)).dot(np.ones((1, len(columns))))
        cov_ret = array_cov_np(ret[-10:], ret_market[-10:])
        ret_market_var = np.nanvar(ret_market[-40:], axis=0)
        factor_orig = pd.Series(cov_ret/ret_market_var, index=columns)
        return factor_orig

    def reform(self, temp_result):
        factor = temp_result.rolling(40).mean() / temp_result.rolling(40).std()
        factor[np.isinf(factor)] = 0
        return factor
