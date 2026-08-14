import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptunelong_longterm_20250925_tnca_2(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "qyh_neptunelong_longterm_20250925_tnca_2"
    fill_na_value = ('industry_median',0)
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务：非流动资产过去1年统计量" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "长周期-财务因子-资产类" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    xdb_data = [
        {
       'name': 'xdb_balancesheet_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 16
    },
    ]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            # finance
            df_balancesheet = database['xdb_balancesheet_cs']
            res = (df_balancesheet['TOT_NON_CUR_ASSETS']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(4).tail(1).mean() - x.tail(4).head(1).mean()).to_frame(name='非流动资产统计量')

            res[self.factor_name] = res['非流动资产统计量']
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
