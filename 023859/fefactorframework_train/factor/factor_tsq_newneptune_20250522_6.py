import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_tsq_newneptune_20250522_6(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250522_6"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "财务-应收/应付账款及票据 4年均值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_balancesheet_cs',
        'lag':16
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_balancesheet = database['xdb_balancesheet_cs']
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].astype('Int64')
                                              >= df_balancesheet['S_INFO_LISTDATE'].astype('Int64')]
            df_balancesheet['S_INFO_DELISTDATE'] = df_balancesheet['S_INFO_DELISTDATE'].fillna(20991231)
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].astype('Int64')
                                              <= df_balancesheet['S_INFO_DELISTDATE'].astype('Int64')]

            # df_balancesheet['report_period'] = df_balancesheet['MDDate'].apply(get_report_period)
            # ==========================================================================================
            # df_balancesheet = df_balancesheet[df_balancesheet['report_period'] == 4]
            res = (df_balancesheet['ACCOUNTS_RECEIVABLE_BILL'] / (1e3+df_balancesheet['ACCOUNTS_PAYABLE'])).groupby(['dt','Ticker']).apply(lambda x : x.tail(16).mean()).to_frame(name = self.factor_name)
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
