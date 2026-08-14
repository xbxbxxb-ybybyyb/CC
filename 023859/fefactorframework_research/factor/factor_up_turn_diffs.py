import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_up_turn_diffs(BaseFactor):
    strategy_name = "neptune"
    factor_name = "up_turn_diffs"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "过去20天内上涨时段的换手率差分之和" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30, #注意为正数
         'column': ['close','turn']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表

    def turn_diffs_stat(self,group):
        group = group.copy()
        group['P_flag'] = group['close'] > group['price_mean3']
        group['up_turn_diffs'] = (group['turn_diff'] * group['P_flag'].astype(int)).rolling(20).sum()
        
        return group[['up_turn_diffs']]


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            data['turn_diff'] = data['turn'].groupby('Ticker').diff()
            data['price_mean3'] = data['close'].groupby('Ticker').transform(lambda x: x.shift(1).rolling(3).mean())
            data['up_turn_diffs'] = data.groupby('Ticker').apply(self.turn_diffs_stat)

            
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = data[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df

