from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import pickle
class RankRoAIndustrialStability(BaseFactor):
    """
    *因子名 : RankRoAIndustrialStability
    *因子功能描述 : 总资产报酬率超出行业平均部分的稳定度，衡量一个企业是否具有长期超过行业对手的成长能力。
    *因子参数 : S_FA_ROA2-总资产报酬率（NI + (1-T)*Interest）/ TotalAssets_TTM ,industry_code_all-申万一级行业代码,is_valid_raw-股票状态
    *因子公式 : (总资产报酬率 - 行业横截面平均) / 总资产报酬率历史标准差
    *作者 : 卢泽宁
    *因子创建日期 : 2020.3.5
    """

    factor_type = "DAY"
    s_wind = 'FactorData.WIND_AShareFinancialIndicator'
    s_indcode = 'FactorData.Basic_factor.sw_indcode1'
    s_is_valid_raw = 'FactorData.Basic_factor.is_valid_raw'
    depend_data =[s_wind, s_indcode, s_is_valid_raw]    
    financial_lag = 800
    # reform_window = 20
    def calc_single(self, database):
        industry_code_all = database.depend_data[self.s_indcode].iloc[-1]
        wind = database.depend_data[self.s_wind]
        is_valid_raw = database.depend_data[self.s_is_valid_raw].iloc[-1]
        # ocf2or= wind[self.s_ocf2or].unstack()
        RoA = wind['S_FA_ROA2'].unstack()
        # GRPS = wind[self.s_GRPS].unstack()
        # GRPS = GRPS.fillna(method = 'ffill').reindex(index = EBITPS.index, columns = industry_code_all.index)
        RoA = RoA.fillna(method = 'ffill').reindex(columns = industry_code_all.index)
        factor = RoA
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
        factor = factor_rank
        factor[is_valid_raw == 0] = np.nan
        # factor = factor/factor.rolling(window=d,min_periods=1).mean()
        # factor[np.isinf(factor)] = np.nan
        return factor
    
    def reform(self, temp_result):
        # factor = temp_result / temp_result.rolling(self.reform_window, 1).mean()
        temp_result[np.isinf(temp_result)] = np.nan
        return temp_result
    