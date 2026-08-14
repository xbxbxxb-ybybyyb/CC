import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名：AbsRet2Deal
* 因子功能描述：日内每笔成交贡献的收益率
* 因子参数：[MinuteHigh]: 分钟最高价
           [MinuteLow]: 分钟最低价
           [MinuteOpen]: 分钟开盘价
           [dealnum]: 成交笔数

* 作者：周璇
* 因子创建日期：2019.2.1
* 函数修改日期：尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.9
    
'''


class AbsRet2Deal(BaseFactor):
    factor_type = "DAY"
    fix_times = ["1500"]
    depend_data = ["FactorData.Basic_factor.open_adj_minute",
                   "FactorData.Basic_factor.high_adj_minute",
                   "FactorData.Basic_factor.low_adj_minute",
                   "FactorData.Basic_factor.dealnum"]
    lag = 0

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        open_minute = single_database.depend_data["FactorData.Basic_factor.open_adj_minute"]
        high_minute = single_database.depend_data["FactorData.Basic_factor.high_adj_minute"]
        low_minute = single_database.depend_data["FactorData.Basic_factor.low_adj_minute"]
        dealnum = single_database.depend_data["FactorData.Basic_factor.dealnum"]

        arr = (high_minute.values - low_minute.values) / open_minute.values
        re = pd.DataFrame(arr, index=open_minute.index, columns=open_minute.columns)
        re_sum = abs(re).sum(axis=0)

        ans = re_sum / dealnum.iloc[-1, :]

        return ans