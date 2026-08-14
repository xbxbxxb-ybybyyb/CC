from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import pickle
class RankEBITPSChg(BaseFactor):
    """
    *因子名 : RankEBITPSChg
    *因子功能描述 : 每股息税前利润在行业内排名上升的幅度，成长越快的企业估值空间的提高越大
    *因子参数 : EBITPS-每股息税前利润 ,industry_code_all-申万一级行业代码,is_valid_raw-股票状态
    *作者 : 卢泽宁
    *因子创建日期 : 2020.2.12
    """

    factor_type = "DAY"
    s_wind = 'FactorData.WIND_AShareFinancialIndicator'
    s_EBITPS = 'S_FA_EBITPS'
    s_GRPS = 'S_FA_GRPS'
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
        EBITPS = wind[self.s_EBITPS].unstack()
        # GRPS = wind[self.s_GRPS].unstack()
        # GRPS = GRPS.fillna(method = 'ffill').reindex(index = EBITPS.index, columns = industry_code_all.index)
        EBITPS = EBITPS.fillna(method='ffill').reindex(columns = industry_code_all.index)
        factor = EBITPS
        industry_code = list(pd.Series(np.unique(industry_code_all.fillna('nan').values.flatten())).dropna())
        factor_rank = pd.Series(index=factor.columns)
        for ind in industry_code:
            factor_ind = factor.iloc[:, industry_code_all.values == ind].rank(ascending=True,pct=True, axis=1)
            factor_hist_mean = factor_ind.iloc[:-1].mean()
            factor_ind = (factor_ind.iloc[-1] - factor_hist_mean)
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
