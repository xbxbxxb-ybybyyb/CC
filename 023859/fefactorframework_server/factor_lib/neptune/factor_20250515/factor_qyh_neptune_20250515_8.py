import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptune_20250515_8(BaseFactor):
    owner = 'qyh'
    strategy_name = "neptune"
    factor_name = 'qyh_neptune_20250515_8'
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "amp 60 波动" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'close', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/close.h5',
         'lag': 80,
         'column': []
    },
        {'name': 'low', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/low.h5',
         'lag': 80,
         'column': []
    },
        {'name': 'high', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/high.h5',
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
            df_low = database['low']
            df_high = database['high']
            #
            def f_calc_sum(factor_series):
                return factor_series[~np.isnan(factor_series)].sum()

            def f_calc_cct(factor_series):
                if abs(f_calc_sum(factor_series)) > 1e-8:
                    return f_calc_sum(factor_series ** 2) / (f_calc_sum(factor_series) ** 2)
                else:
                    return np.nan
            df_pre = df_close.T.ffill().iloc[-1].T.unstack().shift(1).stack()
            df = (df_high - df_low).divide(df_pre, axis=0)
            res = (df).max(axis=1)
            res = res.unstack().rolling(60,1).apply(f_calc_cct).stack().to_frame()
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