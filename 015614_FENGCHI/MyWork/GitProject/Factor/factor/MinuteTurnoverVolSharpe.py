# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform


class MinuteTurnoverVolSharpe(BaseFactor):

    """
    * 因子名：MinuteTurnoverVolSharpe
    * 因子功能描述：计算日内交易额标准差的30日sharpe ratio。
    * 因子参数：MinuteTurnover
    * 作者：姚逸凡
    * 因子创建日期： 2019.1.15
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "DAY"
    # fix_times = ["1500"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    lag = 0
    reform_window = 50

    # def definition(self, MinuteTurnover):

    #     result = self.minute_help(self.minute, 'MinuteTurnoverVolSharpe', MinuteTurnover)
    #     result = self.Mean(result, 50) / self.Stdev(result, 50)

    #     return result

    def Mean(self, DF, lag):

        meanDF = DF.rolling(window=lag, min_periods=1).mean()
        return meanDF

    def Stdev(self,DF, lag):

        stdDF = DF.rolling(window=lag, min_periods=1).std()
        return stdDF

    # def minute(self, MinuteTurnover):

    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteTurnover.index.strftime(fmt))
    #     result_df = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteTurnover.columns)

    #     for date in date_list:
    #         turnover_df = MinuteTurnover.loc[date]

    #         std = turnover_df.std()
    #         if len(std.dropna()) != 0:
    #             result_df.loc[date] = std
    #         else:
    #             result_df.loc[date] = 0.0
    #     return result_df

    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteTurnover.index.strftime(fmt))
        result_df = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteTurnover.columns)

        for date in date_list:
            turnover_df = MinuteTurnover.loc[date]

            std = turnover_df.std()
            if len(std.dropna()) != 0:
                result_df.loc[date] = std
            else:
                result_df.loc[date] = 0.0
        return result_df.iloc[-1,:]

    def reform(self, result):
        result = self.Mean(result, 50) / self.Stdev(result, 50)
        return result

