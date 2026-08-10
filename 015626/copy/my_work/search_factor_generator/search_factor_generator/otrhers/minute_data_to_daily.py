import numpy as np
import pandas as pd


class MinuteDataToDaily:
    """
    把分钟数据根据需要降频到日级别
    """

    def __init__(self, minute_data):
        self.minute_data = minute_data

    def get_trading_days(self):
        """
        获取原始分钟数据包含的所有交易日
        :return: np.ndarray
            原始分钟数据包含的所有交易日
        """
        trading_days = np.unique(self.minute_data.index.date)
        return trading_days

    def get_daily_minute_num(self):
        """
        获取原始分钟数据中的每个交易日有分钟bar
        :return: int
            每个交易日的分钟bar数量
        """
        daily_minute_num = int(self.minute_data.shape[0] / self.get_trading_days().shape[0])
        return daily_minute_num

    def truncated_time_index_num(self, truncated_time):
        """
        由于交易需要等原因，有时候每天的尾盘数据在开发因子时无法使用，需要把这部分数据截去
        这个函数用于确定要截断的时间位于当天的第几分钟
        :param truncated_time: str, e.x.{'14:59'}
            数据截断的时间
        :return:
        """
        daily_minute_num = self.get_daily_minute_num()
        temp_daily_data = self.minute_data.iloc[:daily_minute_num]
        truncated_time_index = pd.Timestamp(str(temp_daily_data.index[0].date()) + ' ' + truncated_time)
        truncated_time_index_num = np.where(temp_daily_data.index == truncated_time_index)[0][0]
        return truncated_time_index_num
