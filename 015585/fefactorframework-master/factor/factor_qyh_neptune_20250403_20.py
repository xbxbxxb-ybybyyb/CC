import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptune_20250403_20(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_20250403_20"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "PB5/10" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'AShareEODDerivativeIndicator', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5',
         'lag': 400, # 注意为正数
         'column': ['S_VAL_PE','S_VAL_PB_NEW','S_VAL_PE_TTM','S_VAL_PCF_OCF','S_VAL_PCF_OCFTTM','S_VAL_PCF_NCF','S_VAL_PCF_NCFTTM','S_VAL_PS','S_VAL_PS_TTM',
                    'S_DQ_FREETURNOVER','S_PRICE_DIV_DPS','NET_PROFIT_PARENT_COMP_TTM','NET_PROFIT_PARENT_COMP_LYR','NET_ASSETS_TODAY','NET_CASH_FLOWS_OPER_ACT_TTM',
                    'NET_CASH_FLOWS_OPER_ACT_LYR','OPER_REV_TTM','OPER_REV_LYR','NET_INCR_CASH_CASH_EQU_TTM','NET_INCR_CASH_CASH_EQU_LYR',]
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['AShareEODDerivativeIndicator'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['AShareEODDerivativeIndicator'] # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            def f_calc_std(factor_series):
                factor_series = factor_series[~np.isnan(factor_series)]
                return np.std(factor_series, ddof=1)
            df_ori['factor'] = df_ori['S_VAL_PB_NEW']
            df_ori[self.factor_name] = df_ori['factor'].unstack().rolling(5,1).max().stack() / \
                                       df_ori['factor'].unstack().rolling(10,1).apply(f_calc_std).stack().apply(lambda x : round_(x,5)).replace(0,np.nan)
            df_ori[self.factor_name] = df_ori[self.factor_name].apply(lambda x : 1e5 if x > 1e5 else -1e5 if x < -1e5 else x)
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
