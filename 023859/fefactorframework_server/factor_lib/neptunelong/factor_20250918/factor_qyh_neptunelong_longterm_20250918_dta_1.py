import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptunelong_longterm_20250918_dta_1(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "qyh_neptunelong_longterm_20250918_dta_1"
    fill_na_value = ('industry_median',0)
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务：递延所得税资产过去1年统计量" # 因子逻辑解释
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
            def f_calc_change(fin_series):
                if fin_series.empty:
                    return np.nan
                else:
                    return fin_series.head(1).mean() - fin_series.tail(1).mean()
            df_balancesheet = database['xdb_balancesheet_cs']
            res = (df_balancesheet['DEFERRED_TAX_ASSETS']).groupby(['dt','Ticker'])\
                .apply(lambda x : f_calc_change(x.tail(4))).to_frame(name='dta统计量')

            res[self.factor_name] = res['dta统计量']
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
