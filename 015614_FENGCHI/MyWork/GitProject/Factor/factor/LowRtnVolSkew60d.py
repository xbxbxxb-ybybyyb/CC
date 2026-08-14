import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

"""
*因子名 : LowRtnVolSkew60d
*因子描述 : 过去三个月内收益率较低成交量的负偏度值
*因子逻辑 : 探求收益较低行情下缩量的程度
*因子参数 : 日频收盘价、成交量与复权因子
*作者 : 沈天琦
*因子创建日期 : 2020.02.18
"""

class LowRtnVolSkew60d(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.volume", "FactorData.Basic_factor.adjfactor"]

    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 60
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置

    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        df_volume = database.depend_data['FactorData.Basic_factor.volume']
        df_close = database.depend_data['FactorData.Basic_factor.close']
        df_adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']

        df_close_adj = df_close * df_adjfactor
        df_volume_adj = df_volume / df_adjfactor

        df_close_rtn = (df_close_adj - df_close_adj.shift(1)) / df_close_adj.shift(1)
        df_is_down = pd.DataFrame(df_close_rtn.values < df_close_rtn.mean(axis=0).values,index=df_close_rtn.index,columns=df_close_rtn.columns)

        s_volume_skew_short = df_volume_adj[df_is_down].skew(axis=0)

        result = -s_volume_skew_short

        return result


