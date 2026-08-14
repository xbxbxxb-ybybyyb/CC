import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
from sklearn.linear_model import LinearRegression

class factor_net_profit_ttm_log_pctchg_min2(BaseFactor):
    strategy_name = "neptune"
    factor_name = "net_profit_ttm_log_pctchg_min2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "使用TTM对数净利润计算的增长率,经过了对增长率为负的情况的稳健化处理" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时

    xdb_data = [{
        'name':'xdb_income_cs',
        'lag':8
    }]

    def quarter_stat_free(self,data,labels):
        cols = ['MDDate'] + labels
        data = data[cols].copy()  # 避免修改原数据

        data.sort_values(by=['Ticker', 'MDDate'], inplace=True)
        for label in labels:
            data[f'{label}_q'] = np.where(data['MDDate'].str[-4:] == '0331',data[label],data[label].diff())
            data[f'{label}_q_log'] = np.sign(data[f'{label}_q']) *np.log(1+abs(data[f'{label}_q']))
            data[f'{label}_ttm'] = data[f'{label}_q'].groupby('Ticker').transform(lambda x: x.rolling(4).sum())
            data[f'{label}_ttm_log'] = data[f'{label}_q_log'].groupby('Ticker').transform(lambda x: x.rolling(4).sum())
        
        cleaned = data.copy()
        cleaned = cleaned.reset_index().set_index(['dt','Ticker','MDDate'])
        for f in cleaned.columns:
            cleaned[f'{f}_pctchg'] = cleaned[f].groupby('Ticker').diff() / abs(cleaned[f].groupby('Ticker').shift(1))
        
        def robust_qoq(data):
            #如果过去三期中最差的情况出现增长率为负，则采用过去两期中较差的值作为因子值
            rolling_min_3 = data.rolling(window=3, min_periods=3).min()
            rolling_min_2 = data.rolling(window=2).min()
            pctchg_list = [col for col in data.columns if 'pctchg' in col]
            for col in pctchg_list:
                condition = rolling_min_3[col] <= 0
                data[f'{col}_min2'] = np.where(condition, rolling_min_2[col], data[col])
            
            return data
    
        cleaned = cleaned.groupby('Ticker').apply(robust_qoq)

        result = cleaned.reset_index().groupby('Ticker').last()
        date = data.index[0][0]

        return date,result


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['xdb_income_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            labels = ['NET_PROFIT_EXCL_MIN_INT_INC']
            date,daily_result = self.quarter_stat_free(data,labels)

            res = daily_result[['NET_PROFIT_EXCL_MIN_INT_INC_ttm_log_pctchg_min2']]
            res = res.rename(columns={'NET_PROFIT_EXCL_MIN_INT_INC_ttm_log_pctchg_min2':self.factor_name})
            res['dt'] = date
            res = res.reset_index().set_index(['dt','Ticker'])

            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
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
