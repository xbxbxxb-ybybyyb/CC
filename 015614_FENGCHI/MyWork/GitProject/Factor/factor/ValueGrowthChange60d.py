from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
import time

class ValueGrowthChange60d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.pe_ttm","FactorData.WIND_AShareFinancialIndicator"]

    financial_lag = 300
    lag = 59

    def calc_single(self,database):

        WIND_AShareFinancialIndicator = database.depend_data['FactorData.WIND_AShareFinancialIndicator']
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
        data = WIND_AShareFinancialIndicator[['ANN_DT','S_QFA_YOYPROFIT']]
        
        ann_dt = data['ANN_DT'].unstack().reindex(pe_ttm.columns,axis=1)
        S_QFA_YOYPROFIT = data['S_QFA_YOYPROFIT'].unstack().reindex(pe_ttm.columns,axis=1)
        
        trading_date_list = pe_ttm.index.tolist()
        yoyprofit=self.get_daily_df_from_quarter_field(ann_dt,S_QFA_YOYPROFIT,trading_date_list)
        value_growth = yoyprofit/pe_ttm
        
        return value_growth.iloc[-1]/value_growth.mean()
    
    
        
        
    def get_daily_df_from_quarter_field(self, stm_issuingdate, df_quarter, trading_date_list):
        stm_issuingdate = stm_issuingdate.astype(float).values
        daily_array = np.nan * np.ones((len(trading_date_list), len(df_quarter.columns)))
        for idx, date in enumerate(trading_date_list):
            daily_array[idx] = pd.DataFrame(np.where(stm_issuingdate <= int(date), df_quarter, np.nan)).fillna(
                method='ffill').iloc[-1].values
        return pd.DataFrame(daily_array, index=trading_date_list, columns=df_quarter.columns)