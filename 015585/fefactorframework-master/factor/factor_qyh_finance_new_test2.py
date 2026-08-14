import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 财务非CS+MD
# 该样例会引发内存超限，目前不在Neptune这样使用
class factor_qyh_finance_new_test2(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_finance_new_test2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 20,
         'column': ['amt']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表

    xdb_data = [{
        'name':'xdb_balancesheet',
        'lag':4
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_balancesheet = database['xdb_balancesheet']
            md_data = database['MD_CHINA_STOCK_DAILY_WIND']
            Ticker = df_balancesheet.index[0][1] if len(df_balancesheet) > 0 else np.nan
            res1 = (df_balancesheet['FIX_ASSETS'] + df_balancesheet['TOT_CUR_ASSETS']).tail(4).sum()
            res2 = md_data['amt'].unstack().rolling(5,1).max().iloc[-1]
            res2 = res2[Ticker] if Ticker in res2.index else np.nan
            res2 = np.nan if abs(res2) <= 1e-8 else res2
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res1/res2]})
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