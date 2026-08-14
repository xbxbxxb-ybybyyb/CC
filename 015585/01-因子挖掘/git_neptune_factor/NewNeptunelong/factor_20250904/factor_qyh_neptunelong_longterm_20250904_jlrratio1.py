import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptunelong_longterm_20250904_jlrratio1(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "qyh_neptunelong_longterm_20250904_jlrratio1"
    fill_na_value = ('industry_median',0)
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务：净利润ratio" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "短周期-财务因子-盈利能力类" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    xdb_data = [
        {
       'name': 'xdb_income_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 16
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            # finance
            df_income = database['xdb_income_cs']
            col = 'NET_PROFIT_EXCL_MIN_INT_INC'
            df_income[f'{col}_diff'] = df_income.groupby(['dt', 'Ticker'])[col].diff()

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

            df_income['report_period'] = df_income['MDDate'].apply(get_report_period)
            df_income.loc[df_income['report_period'] == 1, f'{col}_diff'] = df_income.loc[
                df_income['report_period'] == 1, col] # 单季度处理
            df_income['净利润率'] = df_income['NET_PROFIT_EXCL_MIN_INT_INC_diff'] / df_income['TOT_OPER_COST'].replace(0,np.nan)
            res1 = (df_income['净利润率']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(1).mean()).to_frame(name=self.factor_name)

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
