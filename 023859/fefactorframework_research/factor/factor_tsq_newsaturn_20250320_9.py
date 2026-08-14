# T-1
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_newsaturn_20250320_9(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "saturn"
    factor_name = "tsq_newsaturn_20250320_9"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "放量时刻波动率" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = []
    xdb_data = [
        {
            'name': 'xdb_tickex',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 1  # 回看日期，N为往前回看1~N天
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
        data = database['xdb_tickex']
        data = filter_930(data)
        data['LastPx'] = data['LastPx'].replace(0, np.nan)
        data['LastPx'] = data['LastPx'].ffill()
        data['ret'] = 100*data['LastPx'].pct_change()
        data['ret_std'] = data['ret'].rolling(100).std()
        data['vol'] = data['TotalVolumeTrade'].diff()
        data['vol'] = data['vol'].replace(0, np.nan)
        data['vol'] = data['vol'].ffill()
        data['vol_ret'] = 100*data['vol'].pct_change()
        data['vol_ret_diff'] = data['vol_ret'].diff()
        TimeIndex = data[data['vol_ret_diff'] > (data['vol_ret_diff'].mean() + data['vol_ret_diff'].std())]['MDTime']
        if data[data['MDTime'].isin(TimeIndex)]['ret_std'].std():
            res = data[data['MDTime'].isin(TimeIndex)]['ret_std'].mean() / data[data['MDTime'].isin(TimeIndex)]['ret_std'].std()
        else:
            res = np.nan
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
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
