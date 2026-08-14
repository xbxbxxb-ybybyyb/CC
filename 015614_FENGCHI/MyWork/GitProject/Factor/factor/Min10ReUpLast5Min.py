import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名 : Min10ReUpLast5Min_13h
* 因子功能描述 : 开盘到上午收盘，计算十分钟分钟均价收益，取最后五分钟正收益均值。表示最后五分钟价格增长速度的快慢，值越小超额越高。
* 因子参数 : MinuteVolume -- 分钟成交量, MinuteTurnover -- 分钟成交额
* 作者 : 徐志鑫
* 因子创建日期 : 2019.08.18
* 函数修改日期 : 尚未修改
* 修改人 ：尚未修改
* 修改原因 : 尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.14
'''


class Min10ReUpLast5Min(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        arr = amt_minute.values / volume_minute.values
        price = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        arr = price.values / price.shift(10).values - 1
        re = pd.DataFrame(arr, index=price.index, columns=price.columns)

        arr = re.values >= 0
        df = pd.DataFrame(arr, index=re.index, columns=re.columns)
        re_up = re[df]

        ans = - np.mean(re_up.iloc[-5:])

        return ans
