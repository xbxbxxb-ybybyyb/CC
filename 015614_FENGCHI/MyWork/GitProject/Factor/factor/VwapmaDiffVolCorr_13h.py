from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class VwapmaDiffVolCorr_13h(BaseFactor):

    '''
    * 因子名称：VwapmaDiffVolCorr_13h
    * 描述：滚动成交均价变动与成交量的相关性（开盘前半小时），中心化后取绝对值再取相反数，5日平均
    * 因子逻辑：成交量对成交均价变动的影响越小（即两者的相关系数绝对值越靠近0），股票收益率越高
    * 因子参数：分钟数据的成交额、成交量
    * 作者：何丰敬
    * 日期：2019.8.16
    * 函数修改日期:尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''

    factor_type = "FIX"
    # fix_times = ["1300"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute"]
    lag = 0
    minute_lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        v = database.depend_data['FactorData.Basic_factor.volume_minute']
        a = database.depend_data['FactorData.Basic_factor.amt_minute']
        # date_list = sorted(np.unique(c.index.strftime('%Y-%m-%d')))
        vwapma = a.iloc[:30].cumsum() / v.iloc[:30].cumsum()  # 滚动成交均价
        corr = Util.array_coef(vwapma.diff(), v.iloc[:30])
        return -(corr - np.ones((corr.shape)) * corr.mean()).abs()  # 相关系数中心化后取绝对值再取相反数

    def reform(self, temp):
        return temp.rolling(window=5).mean()  # 5日均值
