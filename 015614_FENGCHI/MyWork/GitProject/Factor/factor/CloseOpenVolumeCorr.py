import time
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：CloseOpenVolumeCorr
* 因子功能描述：
- 计算公式
    x = RANK(DELTA(LOG(VOLUME), 1))
    y = RANK(CLOSE/OPEN - 1)
    ans = - CORR(x, y, 20)
- 编写逻辑
    量价背离考虑的逻辑。20日volume变化率截面排名，与close对open收益率截面排名，
    再取相关性的相反数
* 因子参数： close_adj_minute, open_adj_minute, volume_minute
* 作者：王海洋
* 因子创建时间： 2019.02.07
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改 
'''


class CloseOpenVolumeCorr(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj",
                   "FactorData.Basic_factor.open_badj",
                   "FactorData.Basic_factor.volume"]
    lag = 20
    minute_lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close = single_database.depend_data["FactorData.Basic_factor.close_badj"]
        open = single_database.depend_data["FactorData.Basic_factor.open_badj"]
        volume = single_database.depend_data["FactorData.Basic_factor.volume"]

        volume_log = np.log(volume)
        volume_log_delta = pd.DataFrame(volume_log.values - volume_log.shift(1).values,
                                        index=volume_log.index,
                                        columns=volume_log.columns)
        volume_log_delta_rank = volume_log_delta.rank(axis=1)

        ret = pd.DataFrame(close.values / open.values - 1, index=close.index,
                           columns=close.columns)
        ret_rank = ret.rank(axis=1)

        ans = - array_coef(volume_log_delta_rank, ret_rank)

        return ans
