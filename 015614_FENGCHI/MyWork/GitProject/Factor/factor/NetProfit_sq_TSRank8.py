from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from scipy.stats import rankdata



class NetProfit_sq_TSRank8(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 
                    'FactorData.WIND_AShareCashFlow',
                    'FactorData.WIND_AShareIncome',
                    'FactorData.WIND_AShareBalanceSheet',
                    'FactorData.Basic_factor.is_valid']
                    
    financial_lag = 1000
    lag = 240

    def calc_single(self, database):

        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        WIND_AShareIncome = database.depend_data['FactorData.WIND_AShareIncome']
        WIND_AShareIncome = WIND_AShareIncome[WIND_AShareIncome['STATEMENT_TYPE'] == 408001000.]

        net_profit = WIND_AShareIncome['NET_PROFIT_INCL_MIN_INT_INC'].unstack().reindex(columns=is_valid.columns)
        
        if '20140831' in net_profit.index:
            print('fuck')
            net_profit = net_profit.drop('20140831')
        
        net_profit_ttm , net_profit_sq = self.trans_ttm(net_profit)

        res = net_profit_sq.rolling(8).apply(lambda x: rankdata(x)[-1]/len(x))
        return res.fillna(method='ffill').iloc[-1][valid]
        
        
        
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

