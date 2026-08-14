import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_qyh_neptune_20250424_9(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_20250424_9"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务-现金流最近3年年报均值" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_cashflow_cs',
        'lag':16
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_cashflow = database['xdb_cashflow_cs']
            df_cashflow = df_cashflow[df_cashflow['ANN_DT'].astype('Int64')
                                              >= df_cashflow['S_INFO_LISTDATE'].astype('Int64')]
            df_cashflow['S_INFO_DELISTDATE'] = df_cashflow['S_INFO_DELISTDATE'].fillna(20991231)
            df_cashflow = df_cashflow[df_cashflow['ANN_DT'].astype('Int64')
                                              <= df_cashflow['S_INFO_DELISTDATE'].astype('Int64')]
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
            df_cashflow['report_period'] = df_cashflow['MDDate'].apply(get_report_period)
            #==========================================================================================
            df_cashflow = df_cashflow[df_cashflow['report_period'] == 4]
            res = df_cashflow.groupby(['dt','Ticker'])['STOT_CASH_INFLOWS_OPER_ACT'].apply(lambda x : x.tail(3).mean()).to_frame(name = self.factor_name)
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