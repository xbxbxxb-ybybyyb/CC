from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
import time

class DavisWin(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.ps_ttm","FactorData.WIND_AShareIncome",
    "FactorData.Basic_factor.total_shares","FactorData.Basic_factor.turn","FactorData.Basic_factor.is_valid"]

    financial_lag = 800
    lag = 5

    def calc_single(self,database):

        ps_ttm = database.depend_data['FactorData.Basic_factor.ps_ttm']
        WIND_AShareIncome = database.depend_data['FactorData.WIND_AShareIncome']
        total_shares = database.depend_data['FactorData.Basic_factor.total_shares']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        
        data = WIND_AShareIncome[['ANN_DT','STATEMENT_TYPE','NET_PROFIT_EXCL_MIN_INT_INC']]
        data = data[data['STATEMENT_TYPE']==408001000]
        ann_dt = data['ANN_DT'].unstack().reindex(turn.columns,axis=1)
        net_profit = data['NET_PROFIT_EXCL_MIN_INT_INC'].unstack().reindex(turn.columns,axis=1)
        
        ttm_data = self.get_ttm_data(net_profit)
        trading_date_list = turn.index.tolist()
        net_profit_ttm=self.get_daily_df_from_quarter_field(ann_dt,ttm_data,trading_date_list)
        eps_ttm = pd.DataFrame(net_profit_ttm.values/total_shares.values/10000.,index=ps_ttm.index,columns=ps_ttm.columns)

        turn_rate_rank = turn.rank(pct=True,axis=1).values
        eps_ttm_rank = eps_ttm.rank(pct=True,axis=1).values
        ps_ttm_rank = ps_ttm.rank(pct=True,axis=1).values

        alpha = (0.5+eps_ttm_rank)/(1 + ps_ttm_rank)/(1+turn_rate_rank)
        alpha = pd.DataFrame(1/alpha,index=ps_ttm.index,columns=ps_ttm.columns)
        result = alpha.rolling(window=self.lag).mean().iloc[-1]
        result[is_valid.iloc[-1]==0]=np.nan

        return -result
    
    
    def get_ttm_data(self,df_quarter):
        df_quarter_value = df_quarter.values
        report_date = df_quarter.index.strftime('%Y%m%d')
        ttm_data = np.nan*np.ones((len(report_date),df_quarter.shape[1]))
        for i,date in enumerate(report_date):
            if date[-4:]=='1231':
                ttm_data[i] = df_quarter_value[i]
            elif date[-4:]=='0930' and i>=4:
                ttm_data[i] = df_quarter_value[i]+df_quarter_value[i-3]-df_quarter_value[i-4]
            elif date[-4:]=='0630' and i>=4:
                ttm_data[i] = df_quarter_value[i]+df_quarter_value[i-2]-df_quarter_value[i-4]
            elif date[-4:]=='0331' and i>=4:
                ttm_data[i] = df_quarter_value[i]+df_quarter_value[i-1]-df_quarter_value[i-4]
        ttm_data = pd.DataFrame(ttm_data,index=df_quarter.index,columns=df_quarter.columns)
        return ttm_data
        
        
    def get_daily_df_from_quarter_field(self, stm_issuingdate, df_quarter, trading_date_list):
        stm_issuingdate = stm_issuingdate.astype(float).values
        daily_array = np.nan * np.ones((len(trading_date_list), len(df_quarter.columns)))
        for idx, date in enumerate(trading_date_list):
            daily_array[idx] = pd.DataFrame(np.where(stm_issuingdate <= int(date), df_quarter, np.nan)).fillna(
                method='ffill').iloc[-1].values
        return pd.DataFrame(daily_array, index=trading_date_list, columns=df_quarter.columns)