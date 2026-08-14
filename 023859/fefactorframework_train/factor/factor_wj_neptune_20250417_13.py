import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
class factor_wj_neptune_20250417_13(BaseFactor):
    strategy_name = "neptune"
    factor_name = "wj_neptune_20250417_13"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wj"  # 开发人员姓名
    factor_explain = "过去60日最高级标准差/收盘价标准差" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80,  # 注意为正数
         'column': ['pct_chg', 'turn', 'close', 'high','amt', 'vwap', 'volume','adjfactor']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD']  # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND']  # 和上面t-1_factor_data的name一致

            df_ori['price_adj'] = df_ori['high'] * df_ori['adjfactor']
            df_ori['price1_adj'] = df_ori['close'] * df_ori['adjfactor']
            df_ori['long'] = (df_ori['price_adj']).unstack().rolling(60, 3).apply(lambda x: np.std(x)).stack()
            df_ori['short'] = (df_ori['price1_adj']).unstack().rolling(60, 3).apply(lambda x: np.std(x)).stack()
            df_ori[self.factor_name] = (df_ori['long']/(1e-3+df_ori['short'])).apply(lambda x: round_(x, 5))  # 矩阵大小不同时，Python精度差异，导致计算值不同
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]]  # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori  # 纯h5文件的T-1_Factor直接返回df