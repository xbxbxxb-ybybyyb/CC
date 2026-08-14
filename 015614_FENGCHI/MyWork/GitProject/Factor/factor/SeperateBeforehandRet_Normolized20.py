from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd



class SeperateBeforehandRet_Normolized20(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.turn", "FactorData.Basic_factor.close",
                   "FactorData.Basic_factor.adjfactor"]
    # depend_factors = ["SeperateBeforehandRetFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 40
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 100

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close'] * adjfactor
        turn = database.depend_data['FactorData.Basic_factor.turn']
        ret = close.pct_change(periods=1, axis=0).dropna(how='all')
        last_turn = turn.shift(1).dropna(how='all')
        ret = ret*last_turn/last_turn

        ret_up = ret[ret > ret.median()]
        last_turn_up = last_turn.copy()
        last_turn_up[ret <= ret.median()] = np.nan

        ret_down = ret[ret < ret.median()]
        last_turn_down = last_turn.copy()
        last_turn_down[ret >= ret.median()] = np.nan

        corr_up = Util.array_coef(ret_up, last_turn_up)
        # corr_up = ret_up.corrwith(last_turn_up)
        corr_up[np.abs(corr_up) > 0.9] = np.nan
        corr_down = Util.array_coef(ret_down, last_turn_down)
        corr_down[np.abs(corr_down) > 0.9] = np.nan
        ans = corr_up-corr_down
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        print('reform process')
        return (temp_result - temp_result.rolling(window=100).mean()) / temp_result.rolling(window=100).std()
