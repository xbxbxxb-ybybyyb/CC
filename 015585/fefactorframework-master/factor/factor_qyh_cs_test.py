import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_cs_test(BaseFactor):
    strategy_name = "saturn"
    factor_name = "qyh_cs_test"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xly"  # 开发人员姓名
    factor_explain = "小于9%" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_1_factor_data = [

    ]
    t_1_factor_data_types = []
    xdb_data = [{
        'name':'xdb_tickex_cs',
        'lag':2
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['xdb_tickex_cs']  # 和上面t-1_factor_data的name一致
            res = df_ori.groupby('Ticker').apply(lambda x : x['LastPx'].mean()).to_frame()
            database['pre_T_N'] = res #
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
            return res