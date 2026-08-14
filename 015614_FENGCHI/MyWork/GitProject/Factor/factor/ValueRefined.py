from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
import pickle as pk
class ValueRefined(BaseFactor):
    """

    *因子名 : ValueRefined
    *因子功能描述 : 计算精细化价值因子，综合考虑pe/ps/roe/pcf_ocf
    *因子参数 : close_adj-收盘价 open_adj-开盘价 is_valid-是否合法
    *函数返回值 : 精细化价值因子
    *作者 : 孙海平
    *因子创建日期 : 2019.1.15
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

    """        
    factor_type = "DAY"
    s_Wind = 'FactorData.WIND_AShareFinancialIndicator'
    # s_Suntime = 'FactorData.SUNTIME_cmb_report_subtable'
    s_pe_ttm = 'FactorData.Basic_factor.pe_ttm'
    s_ps_ttm = 'FactorData.Basic_factor.ps_ttm'
    s_pcf_ttm = 'FactorData.Basic_factor.pcf_ocf_ttm'
    s_free_float_shares = 'FactorData.Basic_factor.free_float_shares'
    s_close = 'FactorData.Basic_factor.close'
    s_is_valid = 'FactorData.Basic_factor.is_valid'
    depend_data = [s_Wind, s_pe_ttm, s_ps_ttm, s_pcf_ttm, s_free_float_shares, s_close, s_is_valid]
    financial_lag = 200 # 保证至少获取到一个中报的财度数据
    reform_window = 20
    
    def calc_single(self, database):
        pe_ttm = database.depend_data[self.s_pe_ttm].iloc[-1]
        ps_ttm = database.depend_data[self.s_ps_ttm].iloc[-1]
        pcf_ttm = database.depend_data[self.s_pcf_ttm].iloc[-1]
        free_float_cap = (database.depend_data[self.s_free_float_shares] * database.depend_data[self.s_close]).iloc[-1]
        is_valid = database.depend_data[self.s_is_valid].iloc[-1]
        # 从database中取得依赖的财务原表
        Wind = database.depend_data[self.s_Wind]
        # 从原表中取出S_FA_ROE_AVG字段。该字段为加权平均ROE=报告期净利润/过去四季度平均净资产
        # 该数据在原表中已经把净资产在12个月上TTM过了，所以不需要自己手动TTM
        roe_ttm_orig = Wind['S_FA_ROE_AVG']
        # 原表数据是一个高维度stacked Series，通过unstack()方法可以去除多余的字段名维度，将原表数据整理成以股票名为列，日期为行的DataFrame
        # 然后再统一原表与日频数据的股票池
        roe_ttm = roe_ttm_orig.unstack().fillna(method = 'ffill').reindex(pe_ttm.index, axis = 1).iloc[-1]
        roe_rank = roe_ttm.rank(pct=True).values
        pe_rank = pe_ttm.rank(pct=True).values
        ps_rank = ps_ttm.rank(pct=True).values
        cap_rank = free_float_cap.rank(pct=True).values
        pcf_ocf_rank = pcf_ttm.rank(pct=True).values
        factor = -(1+pcf_ocf_rank)*(1+pe_rank)*(1+ps_rank)*(2+roe_rank)/(1+cap_rank)
        # print(factor)
        return pd.Series(factor, index = pe_ttm.index)
    
    def reform(self, temp_result):
        return (temp_result - temp_result.rolling(self.reform_window).mean()) / temp_result.rolling(self.reform_window).std()
    

    # def definition(self, roe_ttm, pe_ttm, ps_ttm, free_float_cap, pcf_ocf_ttm, is_valid):

    #     n = 20
    #     roe_rank = roe_ttm.rank(pct=True,axis=1)
    #     pe_rank = pe_ttm.rank(pct=True,axis=1)
    #     ps_rank = ps_ttm.rank(pct=True,axis=1)
    #     cap_rank = free_float_cap.rank(pct=True,axis=1)
    #     pcf_ocf_rank = pcf_ocf_ttm.rank(pct=True,axis=1)

    #     factor = -(1+pcf_ocf_rank)*(1+pe_rank)*(1+ps_rank)*(2+roe_rank)/(1+cap_rank)

    #     factorM = (factor - factor.rolling(window=n).mean())/factor.rolling(window=n).std()
    #     factorM[is_valid==0] = np.nan 

    #     return factorM