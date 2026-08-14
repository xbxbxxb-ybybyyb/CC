# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_PriceVolIndustryDelta(BaseFactor):

    """
    * 因子名：HF_PriceVolIndustryDelta_13h
    * 因子功能描述：当日价格分钟线5分钟波动率，波动率低，说明异常炒作越少，具备较为稳定的超额能力。将因子相对行业的变化率作为因子值
    * 因子参数：  MinuteClose,citicsX_industry_code
    * 作者：刘道一
    * 因子创建日期： 20190715
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.citics_indcode1", "FactorData.Basic_factor.close_minute"]
    lag = 2
    minute_lag = 2
    reform_window = 5

    # def definition(self, MinuteClose,citicsX_industry_code):
    #     result = self.minute_help(self.minute, 'HF_PriceVolIndustryDelta_13hHelp', MinuteClose,citicsX_industry_code)
    #     for i in range(len(result)):
    #         if len(result.iloc[i].dropna())==0:result.iloc[i] = 0.
    #     return -1*result

    def industry_excess_div(self,data,indutry_code_df,date):
        industry_list = indutry_code_df.loc[date].unique()
        for ind_i in industry_list:
            ind_idx_in_series = np.where(indutry_code_df.loc[date]==ind_i)[0]
            data.iloc[:,ind_idx_in_series] = data.iloc[:,ind_idx_in_series].div(data.iloc[:,ind_idx_in_series].mean(axis=1),axis=0)
        return data

    # def minute(self, MinuteClose,citicsX_industry_code):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     compute_date = date_list[-1]
    #     pre_date = date_list[-2]
    #     close_df = MinuteClose.loc[compute_date]
    #     price_std = close_df.rolling(5).std().iloc[5:]

    #     result = self.industry_excess_div(price_std,citicsX_industry_code,pre_date)
    #     return result

    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        citicsX_industry_code = database.depend_data["FactorData.Basic_factor.citics_indcode1"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y%m%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        close_df = MinuteClose.loc[compute_date]
        price_std = close_df.rolling(5).std().iloc[5:]
        result = self.industry_excess_div(price_std,citicsX_industry_code,pre_date)
        return result.iloc[-1,:]

    def reform(self, result):
        for i in range(len(result)):
            if len(result.iloc[i].dropna())==0:result.iloc[i] = 0.
        return -result