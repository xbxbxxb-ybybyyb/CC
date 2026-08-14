# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

"""
    * 因子名：MinVwapHLRateBeta
    * 因子功能描述：计算5分钟最大成交额与成交量的vwap与最高价跟最低价价格比率之间的beta，是一个反转因子，该值越大则越容易往下跌
    * 因子参数：  MinuteClose,MinuteHigh, MinuteLow
    * 作者： 肖倩
    * 因子创建日期： 2019.7.29
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""


def array_beta_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanvar(x, axis=0)  # * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class MinVwapHLRateBetaBias(BaseFactor):
    factor_type = 'FIX'
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                   'FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']
    reform_window = 60

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])
        amt_df = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_df = database.depend_data['FactorData.Basic_factor.volume_minute']
        high_df = database.depend_data['FactorData.Basic_factor.high_minute']
        low_df = database.depend_data['FactorData.Basic_factor.low_minute']
        n = 5
        stk_code = amt_df.columns
        vwap_df = (amt_df.rolling(n, n).max() / volume_df.rolling(n, n).max()).rank(axis=0)
        hl_df = (high_df.rolling(n, n).max() / low_df.rolling(n, n).min()).rank(axis=0)
        res = pd.Series(array_beta_np(hl_df.values, vwap_df.values), index=stk_code)
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(60).mean() - temp_result
        return alpha


    # def definition(self, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume):
    #     res = self.minute_help(self.minute, 'MinVwapHLBeta_14h', MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume)
    #     return -1*self.bias_mean(res,60)

    # def minute(self, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteHigh.index.strftime(fmt))
    #     compute_date = date_list[-1]
    #     amt_df = MinuteTurnover.loc[compute_date]
    #     volume_df = MinuteVolume.loc[compute_date]
    #     high_df = MinuteHigh.loc[compute_date]
    #     low_df = MinuteLow.loc[compute_date]
    #     n=5
    #     vwap_df = (amt_df.rolling(n,n).max() / volume_df.rolling(n,n).max()).rank(axis=0)
    #     hl_df = (high_df.rolling(n,n).max() / low_df.rolling(n,n).min()).rank(axis=0)
    #     res = vwap_df.corrwith(hl_df)*vwap_df.std(axis=0)/hl_df.std(axis=0)
    #     return res
