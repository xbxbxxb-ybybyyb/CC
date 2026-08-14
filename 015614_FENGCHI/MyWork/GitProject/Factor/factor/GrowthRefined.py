# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""

    *因子名 : GrowthRefined
    *因子功能描述 : 计算精细化成长因子，综合考虑3年、5年复合净利润增长率和营收增长率
    *因子参数 : close_adj-收盘价 open_adj-开盘价 is_valid-是否合法
    *函数返回值 : 精细化成长因子
    *作者 : 孙海平
    *因子创建日期 : 2019.1.15
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改
    *版本 : 1.0
    *历史版本 : 无

"""   
class GrowthRefined(BaseFactor):
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.WIND_AShareFinancialIndicator','FactorData.Basic_factor.free_float_shares','FactorData.Basic_factor.close','FactorData.Basic_factor.is_valid']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    reform_window = 5
    financial_lag = 2000

    def calc_single(self, database):

        n_gr_tr = 'S_QFA_CGRGR'
        n_gr_np = 'S_QFA_CGRPROFIT'

        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']

        free_float_cap = free_float_shares * close
        
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        is_valid_one = pd.DataFrame(is_valid.values == 1,index=is_valid.index,columns=is_valid.columns)
        status = is_valid[is_valid_one]

        wind_data = database.depend_data['FactorData.WIND_AShareFinancialIndicator']
        gr_tr = wind_data[n_gr_tr].unstack().fillna(method='ffill')
        gr_tr = gr_tr.reindex(columns=status.columns)
        gr_np = wind_data[n_gr_np].unstack().fillna(method='ffill')
        gr_np = gr_np.reindex(columns=status.columns)

        series_gr_np_5y = pd.Series((gr_np.iloc[-20:].values /100 + 1).cumprod(axis=0)[-1] - 1,index=gr_np.columns)
        series_gr_np_3y = pd.Series((gr_np.iloc[-12:].values /100 + 1).cumprod(axis=0)[-1] - 1,index=gr_np.columns)
        series_cagr_tr_5y = pd.Series(np.power((gr_tr.iloc[-20:].values /100 + 1).cumprod(axis=0)[-1],1/5) - 1,index=gr_tr.columns)
        series_cagr_tr_3y = pd.Series(np.power((gr_tr.iloc[-12:].values /100 + 1).cumprod(axis=0)[-1],1/3) - 1,index=gr_tr.columns)
        
        growth_netprofit_5y_rank = series_gr_np_5y.rank(pct=True)
        growth_cagr_tr_5y_rank = series_cagr_tr_5y.rank(pct=True)

        growth_netprofit_3y_rank = series_gr_np_3y.rank(pct=True)
        growth_cagr_tr_3y_rank = series_cagr_tr_3y.rank(pct=True)
        
        cap_rank = free_float_cap[status.columns].rank(pct=True,axis=1).iloc[-1]

        result_values_1 = (growth_netprofit_5y_rank.values + growth_netprofit_3y_rank.values) + 2
        result_values_2 = (growth_cagr_tr_5y_rank.values + growth_cagr_tr_3y_rank.values) + 1
        result_values_3 = 1 + cap_rank.values

        result = pd.Series(result_values_1*result_values_2/result_values_3, index=cap_rank.index)

        return result       

    def reform(self,temp_result):
        return temp_result.rolling(window=self.reform_window).mean() / temp_result.rolling(window=self.reform_window).std()
    # def definition(self, growth_netprofit_5y, growth_netprofit_3y, growth_cagr_tr_5y, growth_cagr_tr_3y, free_float_cap, is_valid):

    #     n = 5
    #     growth_netprofit_5y_rank = growth_netprofit_5y.rank(pct=True,axis=1)
    #     growth_cagr_tr_5y_rank = growth_cagr_tr_5y.rank(pct=True,axis=1)

    #     growth_netprofit_3y_rank = growth_netprofit_3y.rank(pct=True,axis=1)
    #     growth_cagr_tr_3y_rank = growth_cagr_tr_3y.rank(pct=True,axis=1)
        
    #     cap_rank = free_float_cap.rank(pct=True,axis=1)

    #     factor = (2+(growth_netprofit_5y_rank+growth_netprofit_3y_rank))*(1+(growth_cagr_tr_5y_rank+growth_cagr_tr_3y_rank))/(1+cap_rank)
    #     factorM = factor.rolling(window=n).mean()/factor.rolling(window=n).std()
    #     factorM[is_valid==0] = np.nan 

    #     return factorM