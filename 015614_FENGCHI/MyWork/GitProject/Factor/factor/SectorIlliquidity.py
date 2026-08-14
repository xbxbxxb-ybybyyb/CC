from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time


class SectorIlliquidity(BaseFactor):
    """
     * 因子名：SectorNotionalSharpe
     * 因子功能描述:个股相对所在板块的超额非流动性
     * 因子参数： industry_code_all, amt
     * 作者：姚逸凡
     * 因子创建日期： 2019.2.18
     * 函数修改日期： 尚未修改
     * 修改人： 尚未修改
     * 修改原因：尚未修改
     """

    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt", "FactorData.Basic_factor.close_badj", 
                    "FactorData.Basic_factor.open_badj", "FactorData.Basic_factor.sw_indcode1",]
                
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5


    def Delay(self, DF, lag):
        laggedDF = DF.shift(lag)
        return laggedDF

    def Mean(self, DF, lag):

        meanDF = DF.rolling(window=lag, min_periods=1).mean()
        return meanDF

    def Stdev(self, DF, lag):
        stdDF = DF.rolling(window=lag).std()
        return stdDF

    def calc_single(self, database):
        t1=time.time()

        industryCode = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        amt_by_yuan = database.depend_data['FactorData.Basic_factor.amt']
        open_adj = database.depend_data['FactorData.Basic_factor.open_badj']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        
        return_adj = abs((close_adj - open_adj) / open_adj) / amt_by_yuan
        return_adj = self.Mean(return_adj, 5)
        industryValues = industryCode.stack().unique()
        SectorReturn = pd.DataFrame(np.nan, columns=industryValues, index=[return_adj.index[-1]])

        # for dt in return_adj.index:
        #     for industryValue in industryValues:
        #         industryCode_dt = industryCode.loc[dt, :]
        #         cols = list(industryCode_dt[industryCode_dt == industryValue].index)
        #         if len(cols) > 0:
        #             SectorReturn.at[dt, industryValue] = np.nanmean(return_adj.loc[dt, cols].values)



        for industryValue in industryValues:
            # industryCode_dt = industryCode.loc[dt, :]
            # cols = list(industryCode_dt[industryCode_dt == industryValue].index)
            # if len(cols) > 0:
            #     SectorReturn.at[dt, industryValue] = np.nanmean(return_adj.loc[dt, cols].values)
            # print(return_adj[industryCode.values == industryValue].iloc[-1,].mean())
            SectorReturn.loc[return_adj.index[-1],industryValue] =  return_adj[industryCode.values == industryValue].iloc[-1,].mean()
        # print(SectorReturn)




        AlphaScore = pd.DataFrame(0.0, index=[return_adj.index[-1]], columns=return_adj.columns)
        # print(AlphaScore)
        # for dt in AlphaScore.index:
        #     for stock in AlphaScore.columns:
        #         sector = industryCode.at[dt, stock]
        #         if not np.isnan(sector):
        #             AlphaScore.at[dt, stock] = return_adj.at[dt, stock] - SectorReturn.at[dt, sector]
        # print('cost ', time.time()-t1)

        for stock in AlphaScore.columns:
            sector = industryCode.iloc[-1,:].loc[stock]
            # print(sector)
            if not pd.isnull(sector):
            #     AlphaScore.at[dt, stock] = return_adj.at[dt, stock] - SectorReturn.at[dt, sector]
                # print(return_adj.iloc[-1,:].loc[stock] - SectorReturn[sector].values[0])
                AlphaScore.loc[return_adj.index[-1],stock] = return_adj.iloc[-1,:].loc[stock] - SectorReturn[sector].values[0]

        # print(AlphaScore)

        result = AlphaScore.iloc[-1,:]

        return result







