# coding: utf-8
# Author：fengchi863
# Date ：2022/5/12 21:38

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time




class ZaoYinTrader(BaseFactor):
    """

    *因子名 : ZaoYinTrader
    *因子功能描述 : 计算噪音交易细节因子，即捕捉开盘放量、尾盘收涨的情况
    *因子参数 : close_adj-收盘价 open_adj-开盘价 is_valid-是否合法
    *函数返回值 : 噪音交易细节因子
    *作者 : 孙海平
    *因子创建日期 : 2019.1.15
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.turn","FactorData.Basic_factor.close_badj","FactorData.Basic_factor.open_badj"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 20
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10



    def calc_single(self, database):

        n = 10

        turn = database.depend_data['FactorData.Basic_factor.turn']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        open_adj = database.depend_data['FactorData.Basic_factor.open_badj']

        price_diff = (close_adj - open_adj)/close_adj
        price_diff_rank = price_diff.rank(pct=True, axis=1)
        price_diff_rank = pd.DataFrame(2+price_diff_rank.values, index = price_diff.index, columns = price_diff.columns)

        turn_mean = turn.rolling(window=n).mean()
        turn_diff = (turn - turn_mean)/turn_mean
        turn_diff_rank = turn_diff.rank(pct=True, axis=1)
        turn_diff_rank = pd.DataFrame(1+turn_diff_rank.values, index = turn_diff.index, columns = turn_diff.columns)


        # factor = (2+price_diff_rank)*(1+turn_diff_rank)
        factor = price_diff_rank * turn_diff_rank
        # factorM = factor.rolling(window=n).mean()/factor.rolling(window=n).std()
        factorM = factor.iloc[-n:,].mean()/factor.iloc[-n:,].std()
        # factorM[is_valid==0] = np.nan

        return factorM