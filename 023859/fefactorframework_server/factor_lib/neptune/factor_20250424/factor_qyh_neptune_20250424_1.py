import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
from statsmodels.tsa.stattools import coint

class factor_qyh_neptune_20250424_1(BaseFactor):
    owner = 'qyh'
    strategy_name = "neptune"
    factor_name = 'qyh_neptune_20250424_1'
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "5min冲高程度的10日离散度" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'high', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/high.h5',
         'lag': 80,
         'column': []
    },
        {'name': 'close', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/close.h5',
         'lag': 80,
         'column': []
    },
    ]
    t_1_factor_data_types = ['minute5']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_close = database['close']
            df_high = database['high']
            #
            def f_calc_m2m(factor_series):
                factor_series = factor_series[~np.isnan(factor_series)]
                return factor_series.max() / factor_series.mean() if factor_series.mean() > 0 else np.nan
            df = df_high / df_close
            res = (df).max(axis=1)
            res = res.unstack().rolling(10,2).apply(f_calc_m2m).stack().to_frame()
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