from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class Profitability_IndZscore(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 
                    'FactorData.WIND_AShareCashFlow',
                    'FactorData.WIND_AShareIncome',
                    'FactorData.WIND_AShareBalanceSheet',
                    'FactorData.WIND_AShareFinancialIndicator',
                    'FactorData.Basic_factor.sw_indcode1',
                    'FactorData.Basic_factor.is_valid']
                    
    financial_lag = 1000
    lag = 240

    def calc_single(self, database):

        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        sw_indcode1 = database.depend_data['FactorData.Basic_factor.sw_indcode1'].iloc[-1]

        WIND_AShareCashFlow = database.depend_data['FactorData.WIND_AShareCashFlow']
        WIND_AShareCashFlow = WIND_AShareCashFlow[WIND_AShareCashFlow['STATEMENT_TYPE'] == 408001000.]
        WIND_AShareIncome = database.depend_data['FactorData.WIND_AShareIncome']
        WIND_AShareIncome = WIND_AShareIncome[WIND_AShareIncome['STATEMENT_TYPE'] == 408001000.]
        WIND_AShareBalanceSheet = database.depend_data['FactorData.WIND_AShareBalanceSheet']
        WIND_AShareBalanceSheet = WIND_AShareBalanceSheet[WIND_AShareBalanceSheet['STATEMENT_TYPE'] == 408001000.]
        WIND_AShareFinancialIndicator = database.depend_data['FactorData.WIND_AShareFinancialIndicator']


        roe = WIND_AShareFinancialIndicator['S_FA_ROE_DEDUCTED'].unstack().reindex(columns=is_valid.columns)
        roe_avg = roe.pct_change(4).fillna(method='ffill').iloc[-1]
        
        operprofit = WIND_AShareIncome['OPER_PROFIT'].unstack().reindex(columns=is_valid.columns)
        totasset = WIND_AShareBalanceSheet['TOT_ASSETS'].unstack().reindex(columns=is_valid.columns)

        
        ocf = WIND_AShareCashFlow['NET_CASH_FLOWS_OPER_ACT'].drop_duplicates().unstack().reindex(columns=is_valid.columns)
        icf = WIND_AShareCashFlow['NET_CASH_FLOWS_INV_ACT'].drop_duplicates().unstack().reindex(columns=is_valid.columns)
        fcf = WIND_AShareCashFlow['NET_CASH_FLOWS_FNC_ACT'].drop_duplicates().unstack().reindex(columns=is_valid.columns)
    
        gpoa = operprofit/totasset
        cfoa = (ocf+icf+fcf)/totasset
 
        gpoa_avg = gpoa.pct_change(4).fillna(method='ffill').iloc[-1]
        cfoa_avg = cfoa.pct_change(4).fillna(method='ffill').iloc[-1]
            
        industry = sw_indcode1
        tmp = pd.concat([industry, roe_avg, gpoa_avg, cfoa_avg], axis=1)
        tmp.reset_index(inplace=True)
        tmp.columns = ['stock', 'industry', 'roe_avg', 'gpoa_avg', 'cfoa_avg']
        
        tmp.set_index(['stock', 'industry'], inplace=True)
        tmp =tmp.groupby(level=1).rank(pct=True).mean(axis=1, skipna=True)
        
        tmp =tmp.reset_index()
        tmp.columns = ['stock', 'industry', 'value']
        
        return tmp.set_index('stock')['value']
        