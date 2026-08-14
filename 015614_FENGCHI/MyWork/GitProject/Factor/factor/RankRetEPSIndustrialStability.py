from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import pickle
class RankRetEPSIndustrialStability(BaseFactor):
    """
    *因子名 : RankRetEPSIndustrialStability
    *因子功能描述 : 每股留存收益在行业内的稳定性的排名。留存收益高的企业发展稳定，抗风险能力强，且有更高的分红预期，股份相对稳健增长
    *因子参数 : S_FA_RETAINEDPS-每股留存收益 ,is_valid_raw-股票状态
    *因子公式 : (个股的每股留存收益 - 行业平均) / 个股每股留存收益的标准差, 在行业内百分比排序
    *作者 : 卢泽宁
    *因子创建日期 : 2020.2.24
    """

    factor_type = "DAY"
    s_close = 'FactorData.Basic_factor.close'
    s_indcode1 = 'FactorData.Basic_factor.sw_indcode1'
    s_wind = 'FactorData.WIND_AShareFinancialIndicator'
    s_is_valid_raw = 'FactorData.Basic_factor.is_valid_raw'
    depend_data =[s_close, s_wind, s_indcode1, s_is_valid_raw]    
    financial_lag = 800
    reform_window = 60
    def calc_single(self, database):
        close = database.depend_data[self.s_close].iloc[-1]
        wind = database.depend_data[self.s_wind]
        industry_code_all = database.depend_data[self.s_indcode1].iloc[-1]
        factor = wind['S_FA_RETAINEDPS'].unstack()
        factor = factor.reindex(columns = close.index)
        factor = factor.fillna(method='ffill')
        factor_rank = factor.rank(ascending = True, pct=True)
        industry_code = list(pd.Series(np.unique(industry_code_all.fillna('nan').values.flatten())).dropna())
        factor_rank = pd.Series(index=factor.columns)
        for ind in industry_code:
            factor_ind = factor.iloc[:, industry_code_all.values == ind]
            # 公司相对全行业的超额
            company_excessive = (factor_ind.values.T - factor_ind.mean(axis=1).values).T
            company_excessive = pd.DataFrame(company_excessive, index = factor_ind.index, columns=factor_ind.columns)
            company_std = factor_ind.std(axis=0)
            factor_ind = company_excessive.tail(4).fillna(method='ffill').iloc[-1] / company_std
            factor_rank[factor_ind.index] = factor_ind
        # factor_rank = factor_rank.fillna(method = 'ffill').iloc[-1]
        return factor_rank
    
    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        return temp_result.rolling(self.reform_window,1).mean()
    