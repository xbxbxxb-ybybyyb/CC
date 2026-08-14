import time
import numpy as np
import pandas as pd
from collections import Counter
from xfactor.BaseFactor import BaseFactor
from xfactor.Util import array_coef, rolling_corr
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：ClosePercentUp5d
* 因子功能描述：上行市场下的收盘价百分比5日EMA
* 因子参数：[MinuteClose]: 分钟收盘价
               [close_adj]: 收盘价
               [n]: 回看天数
* 作者：周璇
* 因子创建日期：2019.4.18
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.22
'''


class ClosePercentUp5d(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_adj_minute",
                   "FactorData.Basic_factor.close_badj"]
    lag = 5

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        close_minute = single_database.depend_data["FactorData.Basic_factor.close_adj_minute"]
        close_badj = single_database.depend_data["FactorData.Basic_factor.close_badj"]

        ClosePercent = self.minute(close_minute)
        arr = close_badj.values / close_badj.shift(1).values - 1
        re = pd.DataFrame(arr, index=close_badj.index, columns=close_badj.columns)
        ClosePercentUp5d = ClosePercent[pd.DataFrame(re.values > 0, index=re.index, columns=re.columns)].\
            rolling(window=self.lag, min_periods=1).apply(self.EMA)
        return -ClosePercentUp5d.iloc[-1,:]


    def EMA(self, c):
        c = c[~np.isnan(c)]
        Y = 0
        n = 1
        for ci in c:
            Y = (2 * ci + (n - 1) * Y) / (n + 1)
            n += 1
        return Y

    def minute(self, MinuteClose):
        fmt = '%Y%m%d'
        datelist = np.unique(MinuteClose.index.strftime(fmt))
        ClosePercent = pd.DataFrame(index=datelist, columns=MinuteClose.columns)

        for date in datelist:
            close = MinuteClose.loc[date]
            close_arr = close.values
            result = np.array([np.nan]*close.shape[1])
            for j in range(close.shape[1]):
                mylist = close_arr[:,j]
                if ~np.isnan(close_arr[-1,j]) and Counter(np.isnan(mylist))[0]>=200:
                    ind = np.where(~np.isnan(mylist))[0]
                    sort = np.sort((mylist)[ind])
                    if close_arr[-1,j]<sort[0]:
                        result[j] = (close_arr[-1,j]-sort[0])/abs(sort[0])
                    elif close_arr[-1,j]>=sort[-1]:
                        result[j]=1+(close_arr[-1,j]-sort[-1])/abs(sort[-1])
                    else:
                        bigger_this_data = np.where(sort>=close_arr[-1,j])[0]
                        result[j] = bigger_this_data[0]/(len(sort)+1)
            ClosePercent.loc[date] = result

        ClosePercent=ClosePercent.convert_objects(convert_numeric=True)
        return ClosePercent
