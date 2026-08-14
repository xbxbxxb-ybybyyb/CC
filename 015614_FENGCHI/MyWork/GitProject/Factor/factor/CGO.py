from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class CGO(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.vwap","FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.turn","FactorData.Basic_factor.total_shares","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=99
    reform_window=1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["", ""])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        vwap = database.depend_data['FactorData.Basic_factor.vwap'].copy()
        adj_factor = database.depend_data['FactorData.Basic_factor.adjfactor'].copy()
        vwap = vwap*adj_factor
        turn = database.depend_data['FactorData.Basic_factor.turn'].copy()
        shares = database.depend_data['FactorData.Basic_factor.total_shares'].copy()

        amt_min =data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'].copy(),limit_status,method='minute')
        volume_min = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'].copy(),limit_status,method='minute')
        last_datemin = [i for i in amt_min.index if i.date() == amt_min.index[-1].date()]

        amt_min = amt_min.loc[last_datemin,:]
        volume_min = volume_min.loc[last_datemin,:]

        vwap_adj = vwap
        vwap_last_day = min_forward_adj(amt_min.sum(axis=0, skipna=True)/volume_min.sum(axis=0, skipna=True),date=amt_min.index[-1].date())
        vwap_adj_comp = vwap_adj.append(vwap_last_day, ignore_index=True)
        turn_last_day = volume_min.sum(axis=0)/shares.iloc[-1, :]/100
        turn_comp = turn.append(turn_last_day, ignore_index=True)
        turn_comp = pd.DataFrame(turn_comp.values/100, columns=turn_comp.columns, index=turn_comp.index)
        turn_comp[turn_comp.values == 0] = np.nan
        remain_turn = pd.DataFrame(1-turn_comp.values, columns=turn_comp.columns, index=turn_comp.index)
        weight_of_vwap = pd.DataFrame(columns=turn_comp.columns, index=turn_comp.index)
        for i in range(turn_comp.shape[0]):
            if i < turn_comp.shape[0]:
                weight_of_vwap.iloc[i, :] = turn_comp.iloc[i, :] * remain_turn.iloc[(i+1):, :].prod(axis=0, skipna=True)
            else:
                weight_of_vwap.iloc[i, :] = turn_comp.iloc[i, :]
        weight_of_vwap_unified = weight_of_vwap/weight_of_vwap.sum(axis=0, skipna=True)
        cost = (weight_of_vwap_unified * vwap_adj_comp).sum(axis=0, skipna=True)
        ans = vwap_adj_comp.iloc[-1, :]/cost - 1
        return ans

    def reform(self, temp_result):
        
        alpha = temp_result
        alpha = alpha.rolling(self.reform_window, min_periods=int(self.reform_window/2)).mean()
        return alpha


