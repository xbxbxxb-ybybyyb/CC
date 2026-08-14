import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_qyh_neptune_20250424_15(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_20250424_15"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务-最近三年年报职工薪酬增长率" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_balancesheet',
        'lag':12
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            # finance
            df_balancesheet = database['xdb_balancesheet']
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].apply(int)
                                              >= df_balancesheet['S_INFO_LISTDATE'].apply(int)]
            df_balancesheet['S_INFO_DELISTDATE'] = df_balancesheet['S_INFO_DELISTDATE'].fillna(20991231)
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].apply(int)
                                              <= df_balancesheet['S_INFO_DELISTDATE'].apply(int)]
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
            df_balancesheet['report_period'] = df_balancesheet['MDDate'].apply(get_report_period)
            #
            try:
                res = ((df_balancesheet['EMPL_BEN_PAYABLE']).tail(3).diff(2) / (df_balancesheet['EMPL_BEN_PAYABLE'])).values[-1]
            except:
                res = 0
            res = -0.8 if res < -0.8 else 3 if res > 3 else res
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
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