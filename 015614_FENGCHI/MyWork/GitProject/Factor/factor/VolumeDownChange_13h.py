from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VolumeDownChange_13h(BaseFactor):

    """
    *因子名：VolumeDownChange_13h
    *因子功能描述：当日截至13:00分钟收益为负时的成交量，与前一日该值的变化率。
    衡量卖方量能，该值越小，说明当日卖方量能较弱，当日交易过半后市动量效应更明显，后市仍可能是买方市场。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.6.28
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.close_adj_minute", "FactorData.Basic_factor.volume_adj_minute"]
    lag = 0
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        c = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        v = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        dates = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        shape = c.loc[dates[-1]].shape
        vv = []
        for d in dates:
            r = c.loc[d].iloc[:shape[0]] / c.loc[d].iloc[:shape[0]].shift(1) - np.ones(shape)
            vv.append(v.loc[d].iloc[:shape[0]][r<np.zeros(shape)].sum())
        vvv = vv[-1] / vv[-2] - np.ones(vv[-1].shape)
        return -vvv