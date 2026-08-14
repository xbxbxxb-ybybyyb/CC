import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_demo_finance_mixed(BaseFactor):
    strategy_name = "neptune"
    factor_name = "demo_finance_mixed"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_balancesheet_cs',
        'lag':16
    },
        {
        'name': 'xdb_income_cs',
        'lag': 16
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_bs = database['xdb_balancesheet_cs']
            df_income = database['xdb_income_cs']
            #==========================================================================================
            df_bs = pd.merge(df_bs.reset_index(), df_income[['NET_PROFIT_EXCL_MIN_INT_INC','MDDate']].reset_index(), left_on=['dt','Ticker','MDDate'], right_on=['dt','Ticker','MDDate'], how='left').set_index(['dt','Ticker'])
            df_bs['factor'] = df_bs['NET_PROFIT_EXCL_MIN_INT_INC'] / (df_bs['TOT_ASSETS'] - df_bs['TOT_LIAB']).replace(0,np.nan)
            res = df_bs.groupby(['dt','Ticker'])['factor'].apply(lambda x : x.tail(3).mean()).to_frame(name = self.factor_name)

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