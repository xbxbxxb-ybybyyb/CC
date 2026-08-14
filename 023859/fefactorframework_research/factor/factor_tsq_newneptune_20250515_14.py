import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_tsq_newneptune_20250515_14(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250515_14"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "财务-最近四年资产减值损失" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_income_cs',
        'lag':16
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

            # df_income['report_period'] = df_income['MDDate'].apply(get_report_period)
            # # ==========================================================================================
            # df_income = df_income[df_income['report_period'] == 4]
            res = (df_income['OPER_PROFIT']+df_income['PLUS_NON_OPER_REV']-df_income['LESS_NON_OPER_EXP']).groupby(['dt','Ticker']).apply(lambda x : x.tail(12).std() / (1e-6 + x.tail(12).mean())).to_frame(name = self.factor_name)
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
