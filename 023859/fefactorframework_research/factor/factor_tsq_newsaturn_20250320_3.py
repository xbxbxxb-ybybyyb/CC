# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_newsaturn_20250320_3(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "saturn"
    factor_name = "tsq_newsaturn_20250320_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "卖单盘口击穿时下单额标准差" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "卖单强度-总量强度" # 逻辑类别
    low_cost = "否" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = ['T1mTickfulladdorder']
    xdb_data = []
    t_1_factor_data = []
    #     {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
    #      'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
    #      'lag': 20, #注意为正数
    #      'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap']
    # }]
    t_1_factor_data_types = []#['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            data = database['T1mTickfulladdorder']
            data = filter_930(data)
            data_sell_break = data[data['Sell1Price'].diff() > 0]
            res = (data_sell_break['OrderPrice']*data_sell_break['OrderQty']).std()
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
