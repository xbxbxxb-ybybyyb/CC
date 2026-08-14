from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time




class VolPriceFlyer(BaseFactor):
    
    '''
    * 因子名：VolPriceFlyer
    * 逻辑：该因子为成交量相对于自由流通股本占比与收益率的相关性
    * 因子参数：成交额，自由流通市值，收盘价，is_valid_raw
    * 作者：xust
    * 日期：2019.01.16
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt","FactorData.Basic_factor.close","FactorData.Basic_factor.close_badj","FactorData.Basic_factor.free_float_shares"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 20
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    def calc_single(self, database):

        n=10

        amt_by_yuan = database.depend_data['FactorData.Basic_factor.amt']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        close = database.depend_data['FactorData.Basic_factor.close']
        shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        free_float_cap = close*shares

        turn = amt_by_yuan / free_float_cap
        turn_avg = turn.rolling(window=n, min_periods=n).mean()
        turn_std = turn.rolling(window=n, min_periods=n).std()
        turn_norm = (turn - turn_avg) / turn_std
        # turn_norm = pd.DataFrame((turn.values - turn_avg.values) / turn_std.values, index = turn.index, columns=turn.columns)
        turn_norm[np.isinf(turn_norm)] = np.nan

        
        price = close_adj
        price_avg = price.rolling(window=n, min_periods=n).mean()
        price_std = price.rolling(window=n, min_periods=n).std()
        price_norm = (price - price_avg) / price_std
        # price_norm = pd.DataFrame((price.values - price_avg.values) / price_std.values, index = turn.index, columns=turn.columns)
        price_norm[np.isinf(price_norm)] = np.nan

        # alpha = -1 * price_norm.rolling(window=n, min_periods=n).corr(turn_norm)
        alpha = -1 * Util.array_coef(price_norm.iloc[-n:,], turn_norm.iloc[-n:,])
        return alpha
        