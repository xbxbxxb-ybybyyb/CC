# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_neweuropa_20250123_3(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "jupiter/europa"
    factor_name = "tsq_neweuropa_20250123_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "触发前五分钟十档买卖挂单笔数不平衡" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "买单强度-订单结构" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = ['TTick1s']
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
            data = database['TTick1s']
            data = filter_930(data)
            data = generate_time_delta_930(data)
            levels = np.arange(1,11)
            if len(data):
                data['trigger_time'] = data['MDTime_delta'].iloc[-1]
                data = data[(data['trigger_time'] - data['MDTime_delta']) <= 300 * 1000]
                for i in levels:
                    data[f'imbalance_level_{i}'] = (
                        data[f'Buy{i}NumOrders'] - data[f'Sell{i}NumOrders']
                    ) / (data[f'Buy{i}NumOrders'] + data[f'Sell{i}NumOrders'] + 1e-6)
                res = (data[[f'imbalance_level_{i}' for i in levels]].mean(axis=1)).mean()
            else:
                res = np.nan
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
