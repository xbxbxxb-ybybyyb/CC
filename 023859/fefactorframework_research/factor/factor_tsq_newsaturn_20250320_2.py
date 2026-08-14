# T-1
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_newsaturn_20250320_2(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "saturn"
    factor_name = "tsq_newsaturn_20250320_2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "主动卖单变异系数" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "卖单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = []
    xdb_data = [
        {
            'name': 'xdb_trade',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 3  # 回看日期，N为往前回看1~N天
        }
    ]
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
        data = database['xdb_trade']
        data = filter_930(data)
        data = filter_transaction(data)
        res = 0
        for date in data.index.get_level_values(0).unique():
            data_trans = data.loc[date]
            data_trans = generate_time_delta_930(data_trans)
            data_trans_sell = data_trans[data_trans['TradeBSFlag'] == 2]
            res += data_trans_sell['MDTime_delta'].diff().std() / (data_trans_sell['MDTime_delta'].diff().mean() + 1e-6)
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res/3]})
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
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
