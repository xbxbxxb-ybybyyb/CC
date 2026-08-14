from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import rankdata



class RoeTTM_IndRank(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 
                    'FactorData.WIND_AShareCashFlow',
                    'FactorData.WIND_AShareIncome',
                    'FactorData.WIND_AShareBalanceSheet',
                    'FactorData.Basic_factor.sw_indcode1',
                    'FactorData.Basic_factor.is_valid']
                    
    financial_lag = 365*2
    lag = 240

    def calc_single(self, database):

        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        sw_indcode1 = database.depend_data['FactorData.Basic_factor.sw_indcode1']

        WIND_AShareIncome = database.depend_data['FactorData.WIND_AShareIncome']
        WIND_AShareIncome = WIND_AShareIncome[WIND_AShareIncome['STATEMENT_TYPE'] == 408001000.]
        WIND_AShareBalanceSheet = database.depend_data['FactorData.WIND_AShareBalanceSheet']
        WIND_AShareBalanceSheet = WIND_AShareBalanceSheet[WIND_AShareBalanceSheet['STATEMENT_TYPE'] == 408001000.]

        NetProfit = WIND_AShareIncome['NET_PROFIT_INCL_MIN_INT_INC'].unstack().reindex(columns=is_valid.columns)
        NetProfit_ttm , NetProfit_sq = self.trans_ttm(NetProfit)
        
        Equity = WIND_AShareBalanceSheet['TOT_SHRHLDR_EQY_EXCL_MIN_INT'].unstack().reindex(columns=is_valid.columns)

        Roe_TTM = NetProfit_ttm/( Equity.shift(4)+Equity)/2
        indicators = pd.concat([Roe_TTM.fillna(method='ffill').iloc[-1], sw_indcode1.iloc[-1]], axis=1)
        indicators.columns = ['roe_ttm','sw_indcode1']
        
        new_indicators = indicators.groupby('sw_indcode1').rank(pct=True).mean(axis=1, skipna=True)
        return new_indicators[valid]
            
    def trans_ttm(self, data_df):
        data = data_df.values.T
        data_single_quarter = []
        for i in range(len(data)):
            data_single_quarter_stock = []
            for j in range(len(data[i])):
                if j % 4 !=0 :
                    data_single_quarter_stock.append(data[i][j]-data[i][j-1])
                else:
                    data_single_quarter_stock.append(data[i][j])
            data_single_quarter.append(data_single_quarter_stock)

        data_single_quarter_df = pd.DataFrame(data_single_quarter,columns = data_df.index, index=data_df.columns).transpose()
        data_ttm_df = data_single_quarter_df.rolling(4).sum()
        
        return data_ttm_df, data_single_quarter_df

