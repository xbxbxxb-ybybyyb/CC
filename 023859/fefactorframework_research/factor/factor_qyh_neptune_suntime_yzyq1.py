import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 一致预期
class factor_qyh_neptune_suntime_yzyq1(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_suntime_yzyq1"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'DWD_EXP_FORECASTSECU', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/DWD_EXP_FORECASTSECU/DWD_EXP_FORECASTSECU.h5', #DWD_EXP_FORECASTSECU
         'lag': 80,
         'column':['FORECASTYEAR','FORECASTDATE','FORECASTORTYPE','FORECASTROE']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['SUNTIME'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['DWD_EXP_FORECASTSECU'] # 和上面t-1_factor_data的name一致
            df_yzyq_filter = df_ori[df_ori['FORECASTORTYPE'] > 0].sort_values(['dt', 'Ticker', 'FORECASTYEAR'])
            df_yzyq_filter = df_yzyq_filter.groupby(['dt', 'Ticker']).nth(0)  # 此时形成了每日一条的数据
            # -------------------------------------------------------------------------------------------------------------------
            df_yzyq_filter[self.factor_name] = df_yzyq_filter['FORECASTROE'].unstack().rolling(60,1).mean().stack()
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_yzyq_filter[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
