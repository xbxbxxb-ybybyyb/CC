import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_WTR_aog_fill(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "WTR_aog_fill"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "过去3个月分析师预测目标价与预测时前收盘价的比值的均值,对于没有预测数据的股票根据过去三个月的隔夜收益计算相关系数加权填充" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时

    t_1_factor_data = [
    {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
        'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
        'lag': 110,  # 注意为正数
        'column': ['open','close']
        }]
    t_1_factor_data_types = ['MD']
    xdb_data = [{
        'name':'xdb_reporttargetpriceadj_cs',
        'lag':110
    }]
    

    def corr_stat(self, data, label, tick_list, quantile=None):
        corr = data[label].unstack().corr().loc[tick_list, tick_list]
        mask = np.eye(len(tick_list),dtype=bool)
        corr.values[mask] = 1
        
        if quantile is not None:
            abs_corr_series = np.abs(corr.stack())
            q_val = abs_corr_series.quantile(quantile)
            corr = corr.stack()[abs(corr.stack()) >= q_val].unstack().fillna(0)
        
        n_rows = corr.shape[0]
        mask = np.eye(n_rows, dtype=bool)
        corr.values[mask] = 0
        
        non_zero_abs = np.abs(corr.where(corr != 0, np.nan))
        row_sums = non_zero_abs.sum(axis=1)
        row_sums[row_sums == 0] = 1  
        corr = corr.div(row_sums, axis=0)
        
        return corr.fillna(0)


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['xdb_reporttargetpriceadj_cs']
            md_data = database['MD_CHINA_STOCK_DAILY_WIND']
            md_data['aog'] = md_data['open'] / md_data['close'].groupby('Ticker').shift(1) - 1
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            data['target_price'] = np.where(
            ( ~data['CURRENTTARGETPRICE'].isna()) ,
            data['CURRENTTARGETPRICE'],
            np.where(
                ~data['PREVIOUSTARGETPRICE'].isna(),
                data['PREVIOUSTARGETPRICE'],
                data['CURRENTPRICE']
                ) 
            )
            tick_list = data.index.get_level_values(1).unique()
            dt = data.index.get_level_values(0)[0]
            st = (dt + relativedelta(months=-3)).strftime('%Y%m%d')
            
            tmp = data[data['MDDate'] >= st]
            tmp = tmp.drop_duplicates(subset=['MDDate', 'REPORTID'], keep='first')

            res = (tmp['target_price'] / tmp['CURRENTPRICE']).replace([np.inf,-np.inf],np.nan).groupby('Ticker',group_keys=False).mean()
            res = res.reindex(tick_list)

            test = md_data[(md_data.index.get_level_values(0)<dt)&(md_data.index.get_level_values(0)>=st)]
            corr = self.corr_stat(test,'aog',tick_list)

            fill_result = (corr @ res.fillna(0))
            index = res.index
            tmp_result = np.where(res.isna(),fill_result,res)
            tmp_result = pd.Series(tmp_result,index)

            tmp_result = tmp_result.to_frame(self.factor_name) 
            tmp_result = pd.concat({dt:tmp_result}, names=['dt'])
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = tmp_result[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res
