import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 单独财务数据，非CS
class factor_tsq_newneptune_20250424_32(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250424_32"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "向中央银行借款净增加额" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    xdb_data = [{
        'name':'xdb_cashflow',
        'lag':12
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_income = database['xdb_cashflow']
            df_income = df_income[df_income['ANN_DT']
                                                  .apply(int) >= df_income['S_INFO_LISTDATE'].apply(int)]
            res = df_income['NET_INCR_LOANS_CENTRAL_BANK'].tail(12).max() - df_income['NET_INCR_LOANS_CENTRAL_BANK'].tail(12).min()
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
            res1 = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res1}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)