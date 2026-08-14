import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
*因子名 : HighVolumeCorr10d
*因子功能描述 : 分钟最高价与分钟成交量相关性，取负对数。取十日平均。
*因子参数 : minute_high - 分钟最高价, minute_volume - 分钟成交量
*作者 : 徐志鑫
*因子创建日期 : 2019.01.23

"""

class HighVolumeCorr10d(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.volume_minute"]

    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    # lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    minute_lag = 0
    reform_window = 10
    # fix_times = ["1500"]

    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']
        high_minute = database.depend_data['FactorData.Basic_factor.high_minute']

        corr_series = Util.array_coef(volume_minute, high_minute)
        log_corr = -np.log(corr_series)

        log_corr[np.isinf(log_corr)] = np.nan

        return log_corr

    def reform(self, temp_result):
        return temp_result.fillna(method='ffill').rolling(self.reform_window).mean()

    # def definition(self, minute_high, minute_volume):
    #
    #     ratio = self.minute_help(self.calc_ratio, 'HighVolumeCorr10dHelp', minute_high, minute_volume)
    #     result = ratio.fillna(method='ffill').rolling(10).mean()
    #
    #
    #     return result
    #
    # def calc_ratio(self, minute_high, minute_volume):
    #     fmt = '%Y-%m-%d'
    #     dates = np.unique(minute_volume.index.strftime(fmt))
    #     df_result = pd.DataFrame(index=[pd.Timestamp(date) for date in dates],columns=minute_volume.columns)
    #
    #     for date in dates:
    #         high = minute_high.loc[date]
    #         volume = minute_volume.loc[date]
    #
    #         corr = -np.log(high.corrwith(volume))
    #         corr[np.isinf(corr)] = np.nan
    #
    #         df_result.loc[date] = corr
    #
    #     return df_result

