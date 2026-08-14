# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newsat_20240201_1(BaseFactor):
    owner = 'qyh'
    strategy_name = "saturn/sell"
    factor_name = "qyh_newsat_20240201_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    factor_explain = "T日09:31数据，卖1比买1离lastpx更近的tick数" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ["T1mTickab"]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            tick_df = database['T1mTickab']
            tick_df = filter_930(tick_df)
            database['T1mTickab'] = tick_df
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['T1mTickab']
            tick_df['factor'] = np.sign(abs(tick_df['Sell1Price'] - tick_df['LastPx']) - abs(tick_df['Buy1Price'] - tick_df['LastPx']))
            res = tick_df['factor'].sum()
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
