# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import statsmodels.api as sm

class IndustryNeutralizedTurnoverStd(BaseFactor):
    """
    * 因子名：IndustryNeutralizedTurnoverStd
    * 因子功能描述：计算行业、市值中性化后的换手率标准差。
    * 因子参数： turn, mkt_cap_ard, industry_code_all
    * 作者：姚逸凡
    * 因子创建日期： 2019.1.23
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.turn", "FactorData.Basic_factor.mkt_cap_ard",
    "FactorData.Basic_factor.sw_indcode1"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 10

    def Stdev(self, DF, lag):
        stdDF = DF.rolling(window=lag).std()
        return stdDF

    def calcIndustries(self, industry_code_all):

        industry_list = industry_code_all.stack().unique()

        IndustryMark = {}
        for industry in industry_list:

            tmp = pd.DataFrame(np.where(industry_code_all.values == industry,1,0),index=industry_code_all.index, columns=industry_code_all.columns)
            IndustryMark[industry] = tmp

        for key in IndustryMark.keys():
            key = (str)((int)(key))
        industry_list = [(str)((int)(i)) for i in industry_list]

        return IndustryMark, industry_list

    def calcReturnResidual(self, returnResidual, currentFactor):

        index_ = returnResidual.index
        neutralized_df = pd.DataFrame(np.nan, index=returnResidual.index, columns=returnResidual.columns)

        for dt in index_:
            currentfactor = currentFactor.loc[dt]
            ret = returnResidual.loc[dt]
            currentfactor_part = currentFactor.loc[dt]
            ret_part = returnResidual.loc[dt]

            y = np.array(ret).T
            X = np.c_[np.array(currentfactor).reshape(len(currentfactor), 1)]

            y_part = np.array(ret_part).T
            X_part = np.c_[np.array(currentfactor_part).reshape(len(currentfactor_part), 1)]
            model = sm.OLS(y_part, X_part, missing='drop')
            est = model.fit()
            excess = y - est.predict(X)
            neutralized_df.loc[dt] = excess

        return neutralized_df

    def calc_single(self,database):
        turn = database.depend_data['FactorData.Basic_factor.turn']
        size = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        industryCode = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        IndustryMark, industry_list = self.calcIndustries(industryCode)
        neutralized_df = self.calcReturnResidual(turn, size)

        for key in IndustryMark.keys():
            neutralized_df = self.calcReturnResidual(neutralized_df, IndustryMark[key])

        result = -self.Stdev(neutralized_df, 10).iloc[-1,:]
        return result









