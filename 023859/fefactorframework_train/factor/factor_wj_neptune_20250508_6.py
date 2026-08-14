import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 单独财务数据，非CS
class factor_wj_neptune_20250508_6(BaseFactor):
    strategy_name = "neptune"
    factor_name = "wj_neptune_20250508_6"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wj"  # 开发人员姓名
    factor_explain = "近5年，负债合计最大值-中位值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    xdb_data = [{
        'name': 'xdb_balancesheet_cs',
        'lag': 4
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_balancesheet = database['xdb_balancesheet_cs']
            # df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].apply(int) >= df_balancesheet['S_INFO_LISTDATE'].apply(int)]
            res = (df_balancesheet['TOT_LIAB']).groupby(['dt', 'Ticker']).apply(
                lambda x: x.tail(20).max()-x.tail(20).median()).to_frame(name=self.factor_name)
            database['pre_T_N'] = res[[self.factor_name]]  # cs要返回df
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res