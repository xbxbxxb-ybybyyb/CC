import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 财务CS
class factor_qyh_neptune_20250424_8(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_20250424_8"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务-过去2年单季度营收增长率的均值" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_income_cs',
        'lag':9
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_income = database['xdb_income_cs']
            df_income = df_income[df_income['ANN_DT'].apply(int)
                                              >= df_income['S_INFO_LISTDATE'].apply(int)]
            df_income['S_INFO_DELISTDATE'] = df_income['S_INFO_DELISTDATE'].fillna(20991231)
            df_income = df_income[df_income['ANN_DT'].apply(int)
                                              <= df_income['S_INFO_DELISTDATE'].apply(int)]
            # 报告期函数
            def get_report_period(x):
                month = x[4:6]
                if month == '03':
                    return 1
                elif month == '06':
                    return 2
                elif month == '09':
                    return 3
                elif month == '12':
                    return 4
                else:
                    return 5
            df_income['OPER_REV_diff'] = df_income.groupby(['dt','Ticker'])['OPER_REV'].diff()
            df_income['report_period'] = df_income['MDDate'].apply(get_report_period)
            df_income.loc[df_income['report_period'] == 1,'OPER_REV_diff'] = df_income.loc[df_income['report_period'] == 1,'OPER_REV']
            df_income['ratio'] = df_income.groupby(['dt','Ticker'])['OPER_REV_diff'].apply(lambda x : x.diff()/x.shift(1).replace(0,np.nan))
            df_income['ratio'] = df_income['ratio'].apply(lambda x : -0.5 if x < -0.5 else 0.5 if x > 0.5 else x)
            res = df_income.groupby(['dt','Ticker'])['ratio'].apply(lambda x : x.tail(8).mean()).to_frame(name = self.factor_name)
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res