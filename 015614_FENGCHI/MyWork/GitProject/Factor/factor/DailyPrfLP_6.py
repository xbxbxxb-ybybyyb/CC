from xfactor.BaseFactor import BaseFactor
import statsmodels.api as sm
from copy import deepcopy
from datetime import datetime
import time
import pandas as pd
import numpy as np


class DailyPrfLP_6(BaseFactor):
    #  定义因子参数
    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.net_profit_parent_comp_ttm']
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 599


    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        profitttm = database.depend_data['FactorData.Basic_factor.net_profit_parent_comp_ttm']

        def unq_std(group):
            grp_unq = group.drop_duplicates()
            if len(grp_unq)>=6:
                return (grp_unq[-1]-np.mean(grp_unq[-6:-1]))/np.std(grp_unq[-6:-1])
            elif len(grp_unq)>=2:
                return (grp_unq[-1]-np.mean(grp_unq[:-1]))/np.std(grp_unq[:-1]) if np.std(grp_unq[:-1])!=0 else 0
            else:
                return np.nan
        profitttm = profitttm.drop_duplicates()
        profitttm_LP = profitttm.apply(unq_std)
        minute_alpha=profitttm_LP
        return minute_alpha
