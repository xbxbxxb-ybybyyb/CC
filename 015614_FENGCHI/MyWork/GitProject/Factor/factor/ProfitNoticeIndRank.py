from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class ProfitNoticeIndRank(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 
                    'FactorData.WIND_AShareProfitNotice',
                    'FactorData.Basic_factor.sw_indcode1',
                    'FactorData.Basic_factor.is_valid']
                    
    financial_lag = 1000
    lag = 240


    def calc_single(self, database):

        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        sw_indcode1 = database.depend_data['FactorData.Basic_factor.sw_indcode1']

        WIND_AShareProfitNotice = database.depend_data['FactorData.WIND_AShareProfitNotice']
        WIND_AShareProfitNotice = WIND_AShareProfitNotice.reset_index()
        WIND_AShareProfitNotice
        WIND_AShareProfitNotice['S_PROFITNOTICE_DATE'] = [str(int(e)) for e in WIND_AShareProfitNotice['S_PROFITNOTICE_DATE']]
        WIND_AShareProfitNotice['S_PROFITNOTICE_DATE'] =pd.to_datetime(WIND_AShareProfitNotice['S_PROFITNOTICE_DATE'] )
        WIND_AShareProfitNotice = WIND_AShareProfitNotice[WIND_AShareProfitNotice['S_PROFITNOTICE_DATE']< pd.to_datetime(is_valid.index[-1]) ]

        aa = WIND_AShareProfitNotice.groupby(['stock', 'S_PROFITNOTICE_DATE'])['date'].max()
        aa = aa.reset_index().set_index(['stock', 'S_PROFITNOTICE_DATE', 'date']).index
        p = WIND_AShareProfitNotice.set_index(['stock', 'S_PROFITNOTICE_DATE', 'date'])
        p = p.loc[aa]
        p['variation']=((p['S_PROFITNOTICE_CHANGEMAX']+p['S_PROFITNOTICE_CHANGEMIN'])/2)
        p['variation'][p['variation'].isnull()] = np.inf
        variation = p.reset_index().pivot(index = 'S_PROFITNOTICE_DATE', columns = 'stock', values='variation').fillna(method='ffill')
        variation[np.isinf(variation)] = np.nan

        is_valid.index = pd.to_datetime(is_valid.index)

        variation.index = pd.to_datetime(variation.index)
        variation = variation.reindex(index= is_valid.index, columns =is_valid.columns)
        variation = variation.stack().reset_index()
        variation.columns = ['date', 'stock' , 'variation']
        
        ind = sw_indcode1.stack()
        ind = ind.reset_index()
        ind.columns= ['date', 'stock', 'industry']
        ind['date']= pd.to_datetime(ind['date'])

        variation_ind = variation.merge(ind, on=['date', 'stock'])
        variation_ind['variation_indrank'] = variation_ind.groupby(['industry','date'])['variation'].rank(pct=True)

        factor = variation_ind.set_index(['date', 'stock'])['variation_indrank'].unstack()

        return factor.iloc[-1]
        
