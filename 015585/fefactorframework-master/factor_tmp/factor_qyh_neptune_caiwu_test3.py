import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 纯财务
class factor_qyh_neptune_caiwu_test3(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_caiwu_test3"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    finance_data = [
        {'name': 'AShareBalanceSheet', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5',
         'lag': 1300, #注意为正数，是按交易日而非报告期
         'column': ['ANN_DT', 'STATEMENT_TYPE', 'FIX_ASSETS', 'TOT_CUR_ASSETS',]
    },
        {'name': 'AShareIncome', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5',
         'lag': 1300, #注意为正数，是按交易日而非报告期
         'column': ['ANN_DT', 'STATEMENT_TYPE', 'OPER_REV',]
    },
    ]  # 财务数据，格式如上
    t_1_factor_data_types = ['FINANCE'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            def f_calc_sum(factor_series):
                return factor_series[~np.isnan(factor_series)].sum()
            df_balancesheet = database['AShareBalanceSheet']
            df_income = database['AShareIncome']
            df = pd.merge(df_balancesheet,df_income[['OPER_REV']], left_index=True, right_index=True)
            df[self.factor_name] = ((df['FIX_ASSETS'] + df['TOT_CUR_ASSETS']) / df['OPER_REV']).unstack().rolling(12,1).apply(f_calc_sum).stack()
            res = df[['ANN_DT', self.factor_name]]  # 必须返回ANN_DT和因子值两列
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
