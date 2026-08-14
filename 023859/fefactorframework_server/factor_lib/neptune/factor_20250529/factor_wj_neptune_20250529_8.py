import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 单独财务数据，非CS
class factor_wj_neptune_20250529_8(BaseFactor):
    strategy_name = "neptune"
    factor_name = "wj_neptune_20250529_8"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wj"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "少数股东权益合计，20期，（均值-中位值）/振幅" # 逻辑类别
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
            df_balancesheet['report_period'] = df_balancesheet['MDDate'].apply(get_report_period)
            df_balancesheet['factor'] = df_balancesheet['TOT_SHRHLDR_EQY_EXCL_MIN_INT'] - df_balancesheet[
                'TOT_SHRHLDR_EQY_INCL_MIN_INT']
            df_balancesheet['factor_diff'] = (
                    df_balancesheet['TOT_SHRHLDR_EQY_EXCL_MIN_INT'] - df_balancesheet[
                'TOT_SHRHLDR_EQY_INCL_MIN_INT']).diff()
            df_balancesheet['factor_name'] = df_balancesheet.apply(
                lambda x: x['factor_diff'] if x['report_period'] != 1 else x['factor'], axis=1)
            res = (df_balancesheet['factor_name']).groupby(['dt', 'Ticker']).apply(
                lambda x: (x.tail(20).mean() - x.tail(20).median()) / (1e-3 + x.tail(20).max())-x.tail(20).min()).to_frame(
                name=self.factor_name)
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