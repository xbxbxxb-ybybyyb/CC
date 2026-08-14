# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class IndustryExcessIlliqSharpe5d(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_adj_minute","FactorData.Basic_factor.sw_indcode1"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    # fix_times=["1300"]
    minute_lag = 1
    lag =1
    reform_window=20
    def calc_single(self, database):
        data_min = {"FactorData.Basic_factor.amt_minute":database.depend_data['FactorData.Basic_factor.amt_minute'],
                   "FactorData.Basic_factor.close_adj_minute":database.depend_data['FactorData.Basic_factor.close_adj_minute']}
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        MinuteTurnover = data_min['FactorData.Basic_factor.amt_minute']
        MinuteClose = data_min['FactorData.Basic_factor.close_adj_minute']
        industry_code_all = database.depend_data["FactorData.Basic_factor.sw_indcode1"]
        factor = self.minute_help(MinuteClose,MinuteTurnover,industry_code_all)
        return factor
    
    def reform(self,temp_result):
        factor = temp_result
        res =  factor.rolling(5).mean()/factor.rolling(5).std()
        return res   
    def minute_help(self ,MinuteClose,MinuteTurnover,industry_code_all):
        date_list = sorted(np.unique(MinuteClose.index.strftime('%Y%m%d')))
        date = date_list[-1]
        predate = date_list[0]
        if date=='20160107':
            return pd.Series(np.nan, index = MinuteClose.columns)
        industry_today = industry_code_all.loc[predate]
        re = MinuteClose.iloc[-1,:]/MinuteClose.iloc[240,:]-1
        
        illiq = re.abs()/(MinuteTurnover.iloc[240:,:].sum())
        
        tmp = pd.concat([industry_today, illiq], axis = 1)
        tmp.columns =['industry', 'value']
        tmp = tmp.reset_index().set_index(['stock','industry'])
        x = tmp- tmp.groupby('industry').mean() 
        x = x.reset_index().set_index(['stock'])

        return x['value']
