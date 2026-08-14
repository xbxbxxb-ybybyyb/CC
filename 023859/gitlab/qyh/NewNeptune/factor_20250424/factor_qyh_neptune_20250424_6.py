import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptune_20250424_6(BaseFactor):
    owner = 'qyh'
    strategy_name = "neptune"
    factor_name = 'qyh_neptune_20250424_6'
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "low 5m max 的20日cv" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'low', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/low.h5',
         'lag': 80,
         'column': []
    },
    ]
    t_1_factor_data_types = ['minute5']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_low = database['low']
            #
            def f_calc_avg(factor_series):
                return factor_series[~np.isnan(factor_series)].mean()
            def f_calc_cv(factor_series):
                if abs(f_calc_avg(factor_series)) > 0:
                    return np.std(factor_series[~np.isnan(factor_series)], ddof=1) / f_calc_avg(factor_series)
                else:
                    return np.nan
            df = df_low
            res = (df).max(axis=1)
            # .divide(df_amt.max(axis=1).replace(0,np.nan))
            res = res.unstack().rolling(20,2).apply(f_calc_cv).stack().to_frame()
            # res = res.to_frame()
            res.columns = [self.factor_name]
            database['pre_T_N'] = res[[self.factor_name]]  # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori  # 纯h5文件的T-1_Factor直接返回df