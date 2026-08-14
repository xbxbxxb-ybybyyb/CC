from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time




class CEMVsharpe(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt","FactorData.Basic_factor.close_badj","FactorData.Basic_factor.high_badj","FactorData.Basic_factor.low_badj",]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 41
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    
    '''
    * 因子名：CEMVsharpe
    * 逻辑：该因子是之前因子EMVA使用收盘价改进后的夏普率，是一种大幅震荡放量后的反转效应
    * 因子参数：日频数据价量
    * 作者：陈卓
    * 日期：2019.4.3
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''   

    def calc_single(self, database):

        n = 20
        nd = n
        # 提取数据并除以均值
        # hp_valid = high[is_valid_raw==1] * adjfactor
        # lp_valid = low[is_valid_raw==1] * adjfactor
        # close_valid = close[is_valid_raw==1] * adjfactor
        # amt_valid = amt[is_valid_raw==1]
        hp_valid = database.depend_data['FactorData.Basic_factor.high_badj']
        lp_valid = database.depend_data['FactorData.Basic_factor.low_badj']
        close_valid = database.depend_data['FactorData.Basic_factor.close_badj']
        amt_valid = database.depend_data['FactorData.Basic_factor.amt']

        close_valid = close_valid / close_valid.rolling(window=nd, min_periods=nd).mean()
        hp_valid = hp_valid / hp_valid.rolling(window=nd, min_periods=nd).mean()
        lp_valid = lp_valid / lp_valid.rolling(window=nd, min_periods=nd).mean()
        amt_valid = amt_valid / amt_valid.rolling(window=nd, min_periods=nd).mean()
        C = hp_valid - lp_valid
        
        emva = (close_valid - close_valid.shift(1)) * C * amt_valid
        # 计算n日夏普比率
        alpha = emva.rolling(nd, min_periods=10).mean() / emva.rolling(nd, min_periods=10).std()
        # alpha = emva.iloc[-10:,].mean() / emva.iloc[-10:,].std()
        # return -1.*alpha
        return -1.* alpha.iloc[-1,:]