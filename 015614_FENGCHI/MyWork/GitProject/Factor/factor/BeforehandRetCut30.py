from xfactor.BaseFactor import BaseFactor
import statsmodels.api as sm
from copy import deepcopy
from datetime import datetime
import time
import pandas as pd
import numpy as np
from xfactor.FixUtil import min_forward_adj

class BeforehandRetCut30(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.turn"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 30



    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        def get_cut_corr(ret: pd.DataFrame, last_turn: pd.DataFrame):
            result = []
            for i in last_turn.columns:
                temp_ret: pd.Series = ret.loc[:, i].dropna()
                temp_ret = temp_ret[temp_ret < temp_ret.quantile(0.9)]
                temp_last_turn: pd.Series = last_turn.loc[temp_ret.index, i]
                temp_ret = temp_ret * temp_last_turn / temp_last_turn
                temp_last_turn.dropna(inplace=True)
                temp_ret.dropna(inplace=True)
                if len(temp_last_turn.index) >= 10:
                    result.append(temp_last_turn.corr(temp_ret))
                else:
                    result.append(np.nan)
            return result
        adj_factor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close']*adj_factor
        ret = close/close.shift(1)-1
        ret = ret.iloc[1:]
        turn  =database.depend_data['FactorData.Basic_factor.turn']
        last_turn = turn.shift(1).iloc[1:]
        temp_reult = get_cut_corr(ret, last_turn)
        return pd.Series(temp_reult,index =ret.columns)

