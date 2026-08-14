import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# d
class factor_qyh_neptunelong_longterm_20250904_yszk1(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "qyh_neptunelong_longterm_20250904_yszk1"
    fill_na_value = ('industry_median',0)
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务：应收账款diff" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "短周期-财务因子-资产类" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    xdb_data = [
        {
       'name': 'xdb_balancesheet_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 16
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            # finance
            df_balancesheet = database['xdb_balancesheet_cs']
            df_balancesheet['应收账款diff'] = df_balancesheet['ACCT_RCV'].groupby(['dt','Ticker']).diff()
            res1 = (df_balancesheet['应收账款diff']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(1).sum()).to_frame(name=self.factor_name)

            database['pre_T_N'] = res1[[self.factor_name]] # cs要返回df
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
