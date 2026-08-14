import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 卖方预测 这个样例会重复值过高
class factor_qyh_neptune_suntime_mfyc3(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_suntime_mfyc3"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
        'name':'xdb_reportratingadj',
        'lag':250
        }
    ]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        else:
            df_mfyc = database['xdb_reportratingadj'].reset_index()
            df_mfyc['factor'] = df_mfyc['CURRENTGOGOALRATING'] - df_mfyc['PREVIOUSGOGOALRATING']
            res = df_mfyc['factor'].mean()
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res1 = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res1}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
