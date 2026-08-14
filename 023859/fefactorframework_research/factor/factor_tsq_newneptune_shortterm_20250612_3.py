import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_tsq_newneptune_shortterm_20250612_3(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_shortterm_20250612_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "长时间间隔成交买卖不平衡" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "短周期-买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['T1mTransaction']
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        return database

    def prepare_T_data(self, database):
        trans_df = database['T1mTransaction']
        database['T1mTransaction'] = trans_df

        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            data = database['T1mTransaction']
            data = data[(data['MDTime'] >= 93000000) & (data['TradePrice'] > 0)]
            data_time_str = data['MDTime'].astype(str).str.zfill(9)
            data_time_formatted = data_time_str.str[:2] + ':' + data_time_str.str[2:4] + ':' + data_time_str.str[
                                                                                               4:6] + '.' + data_time_str.str[
                                                                                                            6:]
            data['timestamp'] = pd.to_datetime(data_time_formatted, format='%H:%M:%S.%f')
            Buy_Num = len(data[((data['timestamp'].diff()) > '100ms') & (data['TradeBSFlag'] == 1)])
            Sell_Num = len(data[((data['timestamp'].diff()) > '100ms') & (data['TradeBSFlag'] == 2)])
            if (Buy_Num + Sell_Num) != 0:
                res = (Buy_Num - Sell_Num) / (Buy_Num + Sell_Num)
            else:
                res = 0

            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)
