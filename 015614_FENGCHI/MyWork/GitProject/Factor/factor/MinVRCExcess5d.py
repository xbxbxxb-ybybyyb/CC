import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinVRCExcess5d(BaseFactor):
    """
    *因子名：MinVRCExcess5d
    *因子功能描述：收盘价相对任意分钟收盘价收益率的加权方差的5日均值，衡量筹码收益的波动性
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteVolume]: 分钟成交量
               [citicsX_industry_code]: 行业代码
               [n]: 回看天数

    *作者：周璇
    *因子创建日期：2019.6.3
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.citics_indcode1']
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        ind = database.depend_data['FactorData.Basic_factor.citics_indcode1']
        stk_code = close.columns
        ind = ind.iloc[-1]
        r = pd.DataFrame(1 - close.values / close.values[-1], index=close.index, columns=stk_code)
        r_mean_ind = r.T.groupby(ind).mean()
        r_mean_ind = ind.to_frame(name='ind').join(r_mean_ind, on='ind').drop('ind', axis=1).T
        r = r.values - r_mean_ind.values
        w = vol.values / np.nansum(vol.values, axis=0)
        r_mean = np.nansum(r * w, axis=0)
        r_var = np.nansum((r - r_mean) ** 2, axis=0)
        result = pd.Series(-r_var, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(5, 4).mean()
        return alpha
