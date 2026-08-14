from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import pickle
class RankP2UndistributedEPS(BaseFactor):
    """
    *因子名 : RankP2UndistributedEPS
    *因子功能描述 : 复权后的收盘价与每股未分配利润的比值，类似于市盈率。有较高比例未分配利润的股票更容易取得高的股息率。
    *因子参数 : S_FA_UNDISTRIBUTEDPS-每股未分配利润, close-收盘价, adjfactor-复权调整系数
    *因子公式 : 每股未分配利润 / 今日收盘价（复权调整至与报告批露日可比）
    *作者 : 卢泽宁
    *因子创建日期 : 2020.2.26
    """

    factor_type = "DAY"
    s_close = 'FactorData.Basic_factor.close'
    s_adjfactor = 'FactorData.Basic_factor.adjfactor'
    s_indcode1 = 'FactorData.Basic_factor.sw_indcode1'
    s_wind = 'FactorData.WIND_AShareFinancialIndicator'
    s_is_valid_raw = 'FactorData.Basic_factor.is_valid_raw'
    depend_data =[s_close, s_adjfactor, s_wind, s_indcode1, s_is_valid_raw]    
    financial_lag = 400
    lag = 400
    def calc_single(self, database):
        close = database.depend_data[self.s_close]
        close_today = close.iloc[-1]
        adjfactor = database.depend_data[self.s_adjfactor]
        # print(adjfactor.index)
        adj_today = adjfactor.iloc[-1]
        wind = database.depend_data[self.s_wind]
        # industry_code_all = database.depend_data[self.s_indcode1].iloc[-1]
        factor = wind['S_FA_UNDISTRIBUTEDPS']
        factor = factor[~factor.index.duplicated()].unstack() # 过滤重复索引，只保留第一次出现的索引
        factor = factor.reindex(columns = adjfactor.columns)
        ann_dt = wind['ANN_DT']
        ann_dt = ann_dt[~ann_dt.index.duplicated()].unstack()
        ann_dt = ann_dt.reindex(columns = adjfactor.columns)
        ### 获取各支股票最近的公告日期
        ann_dt[factor.isna()] = np.nan # 过滤掉没有批露想要财务指标的公告的批露日期
        # 填充后取最后一行，并把日期格式从浮点数转换为Timestamp
        ann_dt_latest = ann_dt.fillna(method='ffill').iloc[-1].apply(self.convert_date)
        # print('ann_dt', ann_dt_latest)
        # 把批露日期在周末的向前移到周五
        ann_dt_latest[ann_dt_latest.dt.weekday == 5] -= pd.Timedelta('1d')
        ann_dt_latest[ann_dt_latest.dt.weekday == 6] -= pd.Timedelta('2d')

        ## 获取批露日那一天的收盘价复权系数
        adjfactor.index = map(pd.Timestamp, adjfactor.index)
        list_adj = []
        ann_dt_latest = ann_dt_latest.values
        i = 0
        for k,v in adjfactor.iteritems():
            date = ann_dt_latest[i]
            i+=1
            try:
                list_adj.append(v[date])
            except:
                list_adj.append(np.nan)
        adj_ann_date = pd.Series(list_adj, index = adj_today.index)
        # print('adj_ann', adj_ann_date)
        # 将收盘价调整到与公告日那天收盘价可比的水平
        close_adj = close_today / adj_today * adj_ann_date
        factor = factor.fillna(method='ffill').iloc[-1] / close_adj
        factor_rank = factor.rank(pct=True, ascending = True)
        # industry_code = list(pd.Series(np.unique(industry_code_all.fillna('nan').values.flatten())).dropna())
        # factor_rank = pd.Series(index=factor.columns)
        # for ind in industry_code:
            # factor_ind = factor.iloc[-1, industry_code_all.values == ind] / close
            # # 公司相对全行业的超额
            # company_excessive = (factor_ind.values.T - factor_ind.mean(axis=1).values).T
            # company_excessive = pd.DataFrame(company_excessive, index = factor_ind.index, columns=factor_ind.columns)
            # company_std = factor_ind.std(axis=0)
            # factor_ind = company_excessive.tail(4).fillna(method='ffill').iloc[-1] / company_std
            # factor_rank[factor_ind.index] = factor_ind.rank(pct=True)
        # factor_rank = factor_rank.fillna(method = 'ffill').iloc[-1]
        return factor_rank
    
    def reform(self, temp_result):
        temp_result[np.isinf(temp_result)] = np.nan
        return temp_result

    @staticmethod
    def convert_date(d):
        return pd.Timestamp(str(d)[:8])

