import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform

'''
*因子名：ClosePercentRank10d_up
*因子功能描述：上涨市场中收盘价百分比的截面·排序10日均值

*作者：周璇
*因子创建日期：2019.4.10
'''

class ClosePercentRank10d_up(BaseFactor):

    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.open","FactorData.Basic_factor.close_minute"]

    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 10
    minute_lag = 10
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    # reform_window = 10
    # fix_times = ["1500"]

    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self,database):

        data_minute = {"FactorData.Basic_factor.close_minute":database.depend_data['FactorData.Basic_factor.close_minute']}
        minute_data_transform(data_minute,operation=['drop','merge'])

        close_minute = data_minute['FactorData.Basic_factor.close_minute']

        close_p = database.depend_data['FactorData.Basic_factor.close']
        open_p = database.depend_data['FactorData.Basic_factor.open']

        fmt = '%Y-%m-%d'
        datelist = np.unique(close_minute.index.strftime(fmt))
        df_result = pd.DataFrame(index=[pd.Timestamp(date) for date in datelist],columns=close_minute.columns)

        for d in datelist:
            df_result.loc[d] = close_minute.loc[d].rank(pct=True).iloc[-1]

        return -df_result.rank(1)[close_p > open_p].rolling(window=10,min_periods=1).mean().iloc[-1]

