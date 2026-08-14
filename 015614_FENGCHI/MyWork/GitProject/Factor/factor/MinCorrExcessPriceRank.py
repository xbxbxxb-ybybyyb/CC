import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：MinCorrExcessPriceRank_13h
* 因子功能描述：当日截至13:00分钟收益率绝对值相比行业平均的超额和收盘价的秩相关性。
相关性越低，说明价格在高位时波动较稳定，在低位时价格波动剧烈，价低多头活跃，价高空头不活跃，后市有望继续涨。
* 因子参数：[MinuteClose]: 分钟收盘价
           [MinuteOpen]: 分钟开盘价
           [citicsX_industry_code]: 行业代码

* 作者：周璇
* 因子创建日期：2019.7.5
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class MinCorrExcessPriceRank(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.citics_indcode1"]
    lag = 1
    minute_lag = 1

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        citics_indcode1 = single_database.depend_data["FactorData.Basic_factor.citics_indcode1"]

        fmt = '%Y%m%d'
        datelist = sorted(np.unique(close_minute.index.strftime(fmt)))
        compute_date = datelist[-1]
        pre_date = datelist[-2]

        c = close_minute.loc[compute_date]
        o = open_minute.loc[compute_date]

        arr = abs(c.values - o.values) / o.values
        r = pd.DataFrame(arr, index=c.index, columns=c.columns)

        indus_unique = citics_indcode1.loc[pre_date].unique()
        for indus in indus_unique:
            ind = np.where(citics_indcode1.loc[pre_date]==indus)[0]
            r.iloc[:, ind] = r.iloc[:, ind].sub(r.iloc[:,ind].mean(axis=1), axis=0)

        CorrExcessPrice = - array_coef(r.rank(axis=0), c.rank(axis=0))
        return CorrExcessPrice
