from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale

class QualityGrowthIndRank(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 
                    'FactorData.WIND_AShareFinancialIndicator',
                    'FactorData.Basic_factor.sw_indcode1']
                    
    financial_lag = 365*1
    lag = 0
    
    def calc_single(self, database):
        WIND_AShareFinancialIndicator = database.depend_data['FactorData.WIND_AShareFinancialIndicator']
        sw_indcode1 = database.depend_data['FactorData.Basic_factor.sw_indcode1'].iloc[-1]

        roe = WIND_AShareFinancialIndicator['S_QFA_PROFITTOGR'].unstack().fillna(method='ffill').iloc[-1].reindex(index=sw_indcode1.index)
        profitgrowth = WIND_AShareFinancialIndicator['S_QFA_YOYPROFIT'].unstack().fillna(method='ffill').iloc[-1].reindex(index=sw_indcode1.index)

        roe_ind = pd.concat([sw_indcode1, roe],axis=1)
        profitgrowth_ind = pd.concat([sw_indcode1, profitgrowth],axis=1)
        roe_ind.columns = [ 'ind','roe']
        


        profitgrowth_ind.columns = ['ind', 'profitgrowth']
        roe_ind['roe_ind_rank'] = roe_ind.groupby('ind')['roe'].rank(pct=True)
    
        profitgrowth_ind['profitgrowth_ind_rank'] = profitgrowth_ind.groupby('ind')['profitgrowth'].rank(pct=True)
        

        res = roe_ind['roe_ind_rank']+profitgrowth_ind['profitgrowth_ind_rank']

        return res