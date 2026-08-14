# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_qyh_newmim_20240201_1(BaseFactor):
    owner = 'qyh'
    strategy_name = "mimas"
    factor_name = "qyh_newmim_20240201_1"
    factor_explain = "s1均价的max-min" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    fill_na_value = 0
    need_pre_calculate_T_N = False # 纯T日数据不需要pre_T_N
    #
    t_day_data = ["Next1mTickab"]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        return database
    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            tick_df = database['Next1mTickab']
            tick_df = generate_tick_trade_volume(tick_df) # 公共函数
            tick_df = filter_930(tick_df) # 公共函数
            database['Next1mTickab'] = tick_df
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['Next1mTickab']
            tick_df['factor'] = tick_df['TotalValueTrade']/tick_df['TotalVolumeTrade']
            res = tick_df['factor'].max() - tick_df['factor'].min() if round_(tick_df['factor'].mean(),5) > 0 else np.nan
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
