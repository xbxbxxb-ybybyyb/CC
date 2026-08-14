# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd


class NI_SQ_IndustryRank(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    s_Wind = "FactorData.WIND_AShareIncome"
    depend_data = ["FactorData.Basic_factor.sw_indcode1",s_Wind]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    financial_lag = 500
    def calc_single(self, database):
#         report_apply_date = database.depend_data["FactorData.Basic_factor.stm_issuingdate"]
        industry_code_all = database.depend_data["FactorData.Basic_factor.sw_indcode1"]
#         report_applied_date = report_apply_date.apply(pd.to_datetime,format = '%Y%m%d')  
#         NI = database.depend_data['FactorData.Basic_factor.net_profit_excl_min_int_inc']
        WIND_AShareIncome = database.depend_data[self.s_Wind]
        data = WIND_AShareIncome[['ANN_DT','STATEMENT_TYPE','NET_PROFIT_EXCL_MIN_INT_INC']]
        data = data[data['STATEMENT_TYPE']==408001000]
        ann_dt = data['ANN_DT'].unstack().reindex(industry_code_all.columns,axis=1)
        ann_dt = ann_dt.astype('str')
        net_profit = data['NET_PROFIT_EXCL_MIN_INT_INC'].unstack().reindex(industry_code_all.columns,axis=1)
        ttm_data = self.get_ttm_data(net_profit)
        net_profit_ttm = self.trans_quarter2day(ann_dt,ttm_data)
        all_ann_dt = net_profit_ttm.index.tolist()
        industry_code_all.index= [pd.Timestamp(e) for e in industry_code_all.index]
        net_profit_ttm2 = pd.DataFrame(np.nan,index=np.sort(list(set(all_ann_dt).union(set(industry_code_all.index.tolist())))),columns=industry_code_all.columns)
        net_profit_ttm2.loc[all_ann_dt] = net_profit_ttm
        net_profit_ttm2 = net_profit_ttm2.fillna(method='ffill').loc[industry_code_all.index]
                # 如果当前播放的日期超过了报告期却还未到公告披露日，则该支股票该报告期的值会被填为NaN,我们可以有上一个报告期的数据填充它
#         NI = NI.unstack().fillna(method='ffill')
#         # 然后再统一原表与日频数据的股票池
#         NI= NI.reindex(industry_code_all.columns, axis = 1)
#         # 取出最近一个报告期的财务数据，此时roe_ttm变成一个pd.Series
#         NI = NI.iloc[-1]
#         ### 财务数据获取完毕
# #         ttm, sq =self.trans_ttm(NI)
# #         original = self.raw_to_normal(sq, report_applied_date) 

# #         tmp = pd.concat([industry_code_all.stack(),original.stack()], axis =1)
#         print('NI',NI)
#         print('industry',industry_code_all)
        res = net_profit_ttm2.iloc[-1].groupby(industry_code_all.iloc[-1]).rank(pct=True)
        return res

    
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
        
        
    # ann_dt: 公告日
    def trans_quarter2day(self,ann_dt,df_quarter):
        all_ann_dt = np.sort(ann_dt.stack().unique())
        all_ann_dt = [pd.Timestamp(e[:8]) for e in all_ann_dt[all_ann_dt!='nan']]
        
        result = pd.DataFrame(np.nan,index=all_ann_dt,columns=df_quarter.columns)
        
        for report in ann_dt.index:
            temp = pd.DataFrame(np.nan,index=all_ann_dt,columns=df_quarter.columns)
            this_data = {}
            this_data['date'] = ann_dt.loc[report].values
            this_data['stock'] = ann_dt.columns.values
            this_data['value'] = df_quarter.loc[report].values
            this_data = pd.DataFrame.from_dict(this_data).dropna(axis=0)
            this_data['date'] = [pd.Timestamp(e[:8]) for e in this_data['date'].values]
            this_data_pivot = this_data.pivot(index='date',columns='stock',values='value')
            temp.loc[this_data_pivot.index,this_data_pivot.columns] = this_data_pivot.values
            result[~np.isnan(temp)] = temp[~np.isnan(temp)] 
            
        return result