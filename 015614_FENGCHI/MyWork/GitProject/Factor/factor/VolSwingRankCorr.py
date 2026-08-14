import time
import numpy as np
import pandas as pd
from sklearn import linear_model
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：VolSwingRankCorr
* 因子功能描述：
    - 计算公式
        Corr(Rank(volume, 20), Rank(swing, 20), 20)
    - 编写逻辑
        衡量一段时间交易量全市场强度，与振幅全市场强度的相关性，越高则超额收益越高
* 因子参数：volume, swing
* 作者：王海洋
* 因子创建时间： 2019.02.28
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改 
'''


class VolSwingRankCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume",
                   "FactorData.Basic_factor.swing"]
    lag = 20

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume = single_database.depend_data["FactorData.Basic_factor.volume"]
        swing = single_database.depend_data["FactorData.Basic_factor.swing"]

        volume_mkt_strength = volume.rank(axis=1)
        swing_mkt_strength = swing.rank(axis=1)

        ans = array_coef(volume_mkt_strength, swing_mkt_strength)
        ans = pd.Series(-ans.values, index=ans.index)
        return ans
