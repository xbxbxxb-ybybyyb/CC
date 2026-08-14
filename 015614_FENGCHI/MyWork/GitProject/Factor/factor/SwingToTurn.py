from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class SwingToTurn(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.swing",
                   "FactorData.Basic_factor.turn","FactorData.Basic_factor.is_valid_raw"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 19

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        # missing is_valid_raw data
        swing = database.depend_data['FactorData.Basic_factor.swing']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        
        flag = pd.DataFrame((is_valid_raw.values == 1), index=turn.index, columns=turn.columns) 
        swing = swing[flag]
        turn = turn[flag]

        swing_to_turn = swing / turn
        signal = np.square(swing_to_turn).mean(axis = 0)
        signal.name = swing.index[-1]  
        
        return signal


        
