# -*- coding: utf-8 -*-

"""

*因子名 : MinuteUpVar
*因子功能描述 : 计算分钟级高频数据因子，衡量价格上行波动率，越高的组合收益越高。
*因子参数 : MinuteTurnover-成交额 MinuteVolume-成交量 MinuteOpen-开盘价
*函数返回值 : 价格上行波动率因子
*作者 : 孙海平
*因子创建日期 : 2018.12.12
*函数修改日期 : 尚未修改
*修改人 ：尚未修改
*修改原因 :  尚未修改
*版本 : 1.0
*历史版本 : 无

"""

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteUpVar(BaseFactor):
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.open_minute']
    reform_window = 19

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        op = database.depend_data['FactorData.Basic_factor.open_minute']
        stk_code = amt.columns
        op = op.values[0]
        vwap_r = pd.DataFrame(amt.values / vol.values).fillna(method='pad').pct_change().fillna(0)
        vwap_r = vwap_r.values
        result = np.nanvar(np.where(vwap_r > 0, vwap_r, np.nan), axis=0) / np.nanvar(vwap_r, axis=0)
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(20, 1).mean() / temp_result.rolling(20, 1).std()
        return alpha
