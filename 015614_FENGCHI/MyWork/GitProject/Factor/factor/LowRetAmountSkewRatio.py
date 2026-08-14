import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform

'''
* 因子名称：LowRetAmountSkewRatio_13h
* 描述：T-4至T日11:30滚动滚动60分钟平均收益率最低时的成交额偏度 / T-4至T日11:30成交额偏度
* 因子逻辑：股价下跌时段的成交额偏度如果特别大，说明此时出现大额成交的频率比平时高，可能存在超卖的情况
* 因子参数：分钟数据的成交额、成交量，复权因子
* 作者：何丰敬
* 日期：2019.9.22
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
* 迁移作者：015625
* 迁移日期：2020.1.13
'''


class LowRetAmountSkewRatio(BaseFactor):
    factor_type = "FIX"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute"]
    lag = 0
    minute_lag = 4

    def calc_single(self, single_database):
        minute_data_transform(single_database.depend_data, operation=["drop", "merge"])

        volume_minute = single_database.depend_data["FactorData.Basic_factor.volume_adj_minute"]
        amt_minute = single_database.depend_data["FactorData.Basic_factor.amt_minute"]

        arr = amt_minute.values / volume_minute.values
        vwap = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        vwap_re =  pd.DataFrame(vwap.values/vwap.shift(1).values-1, index=vwap.index, columns=vwap.columns) 
        arr = vwap_re.values - vwap_re.mean(axis=1).values.reshape(vwap_re.shape[0], 1)
        excess_re = pd.DataFrame(arr, index=volume_minute.index, columns=volume_minute.columns)

        r_rolling = excess_re.rolling(60).mean()  # (1080. 3574)
        r_rolling_min = r_rolling.min()   # (3574, )
        amount = amt_minute.rolling(60).skew()  # 筛选出滚动60分钟超额收益最低时的成交额偏度

        arr = r_rolling.values == r_rolling_min.values
        flag = pd.DataFrame(arr, index=r_rolling.index, columns=r_rolling.columns)

        arr = amount[flag].mean().values / amt_minute.skew().values
        ans = pd.Series(arr, index=volume_minute.columns)

        return ans
