import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_rank_AOG_demax20(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "rank_AOG_demax20"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "捕捉隔夜收益较大的股票，用截面排序解决时序不可比的问题, 用当日值减去过去20日最大值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30, #注意为正数
         'column': ['open','close']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            
            df_ori['AOG_rank'] = (df_ori['open'] / df_ori['close'].groupby('Ticker',group_keys=False).shift(1)).groupby('dt',group_keys=False).rank()
            df_ori['AOG_rank_max20'] = df_ori['AOG_rank'].groupby('Ticker',group_keys=False).transform(lambda x: x.shift(1).rolling(20).max())
            factor = df_ori['AOG_rank'] - df_ori['AOG_rank_max20']
            factor = factor.groupby('dt',group_keys=False).apply(lambda x:(x-x.mean())/x.std())

            df_ori[self.factor_name] = factor
            
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df

