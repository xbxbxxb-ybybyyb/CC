import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


def array_beta_np(r, r_bench):
    r_bench = np.tile(r_bench.reshape((len(r_bench), 1)), (1, r.shape[1]))
    r[np.isnan(r) | np.isnan(r_bench)] = np.nan
    r_bench[np.isnan(r) | np.isnan(r_bench)] = np.nan
    d_r, d_r_bench = r - np.nanmean(r, axis=0), r_bench - np.nanmean(r_bench, axis=0)
    numerator = np.nanmean(d_r * d_r_bench, axis=0)
    denominator = np.nanvar(r_bench, axis=0)
    beta = numerator / denominator
    beta[np.isinf(beta)] = np.nan
    return beta


class IndustryMidBeta(BaseFactor):
    # 因子名称：IndustryMidBeta
    # 计算公式：计算股票与行业平均收益率的beta，减行业平均beta后取绝对值再取相反数
    # 因子逻辑：与行业beta过高或过低的股票后续表现较差，接近于1的股票表现更好
    depend_data = ['FactorData.Basic_factor.sw_indcode1', 'FactorData.Basic_factor.close_minute']
    reform_window = 20

    def calc_single(self, database):
        ind = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = close.columns
        close = close.values
        r = close[1:] / close[:-1] - 1
        ind = ind.values[-1]
        ind_unique = list(set(ind[~pd.isnull(ind)].tolist()))
        res = np.nan * np.ones(len(stk_code))
        for i in ind_unique:
            r_tmp = r[:, ind == i]
            r_ind = np.nanmean(r_tmp, axis=1)
            res_tmp = array_beta_np(r_tmp, r_ind)
            res_tmp = -np.abs(res_tmp - np.nanmean(res_tmp))
            res[ind == i] = res_tmp
        res = pd.Series(res, index=stk_code)
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window).mean()
        return alpha
