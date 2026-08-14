from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time


class ReverseDistance(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.turn", "FactorData.Basic_factor.amt",
                   "FactorData.Basic_factor.is_valid","FactorData.Basic_factor.free_float_shares",]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 40
    reform_window = 15

# class ReverseDistance(AlphaFactor):
        
    # def definition(self, close_adj, turn, amount, free_float_cap, is_valid):
    def calc_single(self, database):
        
        n = 20
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        close = database.depend_data['FactorData.Basic_factor.close']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        amount=database.depend_data['FactorData.Basic_factor.amt']
        ffs=database.depend_data['FactorData.Basic_factor.free_float_shares']
        is_valid=database.depend_data['FactorData.Basic_factor.is_valid']

        free_float_cap = ffs*close

        close_adj_5 = close_adj.rolling(window=5).mean()
        close_adj_10 = close_adj.rolling(window=10).mean()
        reverse_price = (close_adj.values - (close_adj_5.values+close_adj_10.values)/2)/(close_adj_5.values+close_adj_10.values)/2
        reverse_price = pd.DataFrame(reverse_price, index=close.index, columns=close.columns)

        reverse_price_max = (reverse_price).abs().rolling(window=10).max()
        reverse_price_adj = reverse_price/reverse_price_max
        reverse_price_adj_rank = reverse_price_adj.rank(pct=True,axis=1)

        turn_rank = turn.rank(pct=True,axis=1)
        turn_5 = turn.rolling(window=5).mean()
        reverse_turn = (turn.values - (turn_5.values)/2)/(turn_5.values)/2
        reverse_turn = pd.DataFrame(reverse_turn, index=close.index, columns=close.columns)


        reverse_turn_max = (reverse_turn).abs().rolling(window=10).max()
        reverse_turn_adj = reverse_turn/reverse_turn_max
        reverse_turn_adj_rank = reverse_turn_adj.rank(pct=True,axis=1)

        turn_rate = amount/free_float_cap
        turn_rate_rank = turn_rate.rank(pct=True,axis=1)
        turn_rate_rank = pd.DataFrame(turn_rate_rank.values+1, index=close.index, columns=close.columns)


        alpha = (reverse_price_adj_rank*reverse_turn_adj_rank)*(turn_rate_rank)
        alpha_nd = alpha.iloc[-20:,:].mean()
        # flag = pd.DataFrame((is_valid.values==0), index=close.index, columns=close.columns)
        alpha_nd[(is_valid.iloc[-1,:]==0)] = np.nan 

        return alpha_nd

    def reform(self, temp_result):
        return -temp_result.rolling(window=self.reform_window,min_periods=1).mean()
