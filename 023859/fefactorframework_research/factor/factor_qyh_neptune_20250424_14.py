import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_qyh_neptune_20250424_14(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "qyh_neptune_20250424_14"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务-过去12期应交税费的最大值与最小值的均值" # 因子逻辑解释
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
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].astype('Int64')
                                              >= df_balancesheet['S_INFO_LISTDATE'].astype('Int64')]
            df_balancesheet['S_INFO_DELISTDATE'] = df_balancesheet['S_INFO_DELISTDATE'].fillna(20991231)
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].astype('Int64')
                                              <= df_balancesheet['S_INFO_DELISTDATE'].astype('Int64')]
            #
            res1 = (df_balancesheet['TAXES_SURCHARGES_PAYABLE']).tail(12).max()
            res2 = (df_balancesheet['TAXES_SURCHARGES_PAYABLE']).tail(12).min()
            res = res1 + res2
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res/2]})
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