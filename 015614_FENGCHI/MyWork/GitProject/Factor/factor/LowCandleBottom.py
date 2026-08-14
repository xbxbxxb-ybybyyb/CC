from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import copy



class LowCandleBottom(BaseFactor):
    """
    *因子名：LowCandleBottom
    *因子功能描述： 最低价/candlestick的底部价格
    *因子参数：  low_adj-复权最低价 close_adj-复权收盘价 open_adj-复权开盘价 is_valid-因子合法性标志位
    *作者：刘道一
    *因子创建时间： 2019.01.11
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改 


    """

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.low", "FactorData.Basic_factor.close",
                   "FactorData.Basic_factor.open"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 0
    reform_window = 160

    def calc_single(self, database):
        minute_data_transform(database.depend_data,operation=["drop","merge"])

        close_adj = database.depend_data["FactorData.Basic_factor.close"].iloc[-1]
        open_adj = database.depend_data["FactorData.Basic_factor.open"].iloc[-1]
        low_adj = database.depend_data["FactorData.Basic_factor.low"].iloc[-1]

        candle_bottom = pd.concat([close_adj,open_adj],axis=1).min(axis=1)
        low_candle = (low_adj - candle_bottom)/candle_bottom  
        low_candle[np.isinf(low_candle)] = np.nan
        # candle_bottom = (close_adj[close_adj<open_adj]).fillna(0) + (open_adj[open_adj<close_adj]).fillna(0)
        # low_candle = (low_adj - candle_bottom)/candle_bottom            
        # low_candle[np.isinf(low_candle)] = np.nan
        
        return low_candle

    def  reform(self, temp_result):
        A = temp_result.rolling(self.reform_window,min_periods=5).mean()
        return A
    
