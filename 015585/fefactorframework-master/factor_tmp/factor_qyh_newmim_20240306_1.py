# h5
# 验证新sft的准确性
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newmim_20240306_1(BaseFactor):
    owner = 'qyh'
    strategy_name = "mimas"
    factor_name = "qyh_newmim_20240306_1"
    factor_explain = "挂卖均价对应涨跌幅的首末差异" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    fill_na_value = 0
    need_pre_calculate_T_N = True # 纯T日数据不需要pre_T_N
    #
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['pct_chg', 'open', 'pre_close', 'amt', 'vwap']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    xdb_data = []
    t_day_data = []
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND']
            df_ori = df_ori[df_ori['amt'] > 0]
            df_ori = df_ori[df_ori['open'] > 0]
            df_ori['factor'] = df_ori['open'] / df_ori['amt']
            df_ori['factor'] = df_ori['factor'].apply(lambda x: round_(x, 8))
            df_ori['factor1'] = ((df_ori['factor']).unstack().rolling(20, 1).std().stack() + 1e-5)
            df_ori['factor1'] = df_ori['factor1'].apply(lambda x: round_(x, 8))
            df_ori[self.factor_name] = (df_ori['factor']) / df_ori['factor1']
            df_ori[self.factor_name] = df_ori[self.factor_name].apply(lambda x: round_(x, 6))
            # df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().median(axis=1)
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]]
            return database
    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database
    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
