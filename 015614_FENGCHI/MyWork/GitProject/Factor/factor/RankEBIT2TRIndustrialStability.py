from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import pickle
class RankEBIT2TRIndustrialStability(BaseFactor):
    """
    *因子名 : RankEBIT2TRIndustrialStability
    *因子功能描述  : 毛利率领先同行业可比标的的超额部分的相对稳定性。毛利率是企业经营能力的综合考察，稳定领先于同行的企业更值得投资
    *因子参数 : EBITPS-每股息税前利润, GRPS-每股总收入 ,industry_code_all-申万一级行业代码,is_valid_raw-股票状态
    *作者 : 卢泽宁
    *因子创建日期 : 2020.2.18
    """

    factor_type = "DAY"
    s_wind = 'FactorData.WIND_AShareFinancialIndicator'
    s_EBITPS = 'S_FA_EBITPS'
    s_GRPS = 'S_FA_GRPS'
    s_indcode = 'FactorData.Basic_factor.sw_indcode1'
    s_is_valid_raw = 'FactorData.Basic_factor.is_valid_raw'
    depend_data =[s_wind, s_indcode, s_is_valid_raw]    
    financial_lag = 1200
    # reform_window = 20
    def calc_single(self, database):
        industry_code_all = database.depend_data[self.s_indcode].iloc[-1]
        wind = database.depend_data[self.s_wind]
        is_valid_raw = database.depend_data[self.s_is_valid_raw].iloc[-1]
        EBITPS = wind[self.s_EBITPS].unstack()
        GRPS = wind[self.s_GRPS].unstack()
        GRPS = GRPS.reindex(index = EBITPS.index, columns = industry_code_all.index)
        EBITPS = EBITPS.reindex(columns = industry_code_all.index)
        factor = EBITPS / GRPS
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
        factor_rank[np.isinf(factor_rank)] = np.nan
        return factor_rank
    
    # def reform(self, temp_result):
    #     # factor = temp_result / temp_result.rolling(self.reform_window, 1).mean()
    #     temp_result[np.isinf(temp_result)] = np.nan
    #     return temp_result
    