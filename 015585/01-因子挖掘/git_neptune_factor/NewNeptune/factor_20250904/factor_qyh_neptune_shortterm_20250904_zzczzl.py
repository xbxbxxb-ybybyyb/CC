import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# tail(1) 2分，无效
# tail(4) 17分，负相关
# tail(8) 21分，负相关
# tail(12) 23分
class factor_qyh_neptune_shortterm_20250904_zzczzl(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_shortterm_20250904_zzczzl"
    fill_na_value = ('industry_median',0)
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务：总资产增长率" # 因子逻辑解释
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
            df_balancesheet['总资产增长率'] = df_balancesheet['TOT_ASSETS'].groupby(['dt','Ticker']).diff() / df_balancesheet['TOT_ASSETS'].groupby(['dt','Ticker']).shift(1)
            res1 = (df_balancesheet['总资产增长率']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(8).mean()).to_frame(name=self.factor_name)

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
