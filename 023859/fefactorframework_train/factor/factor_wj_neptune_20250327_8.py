import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_wj_neptune_20250327_8(BaseFactor):
    strategy_name = "neptune"
    factor_name = "wj_neptune_20250327_8"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "wj"  # 开发人员姓名
    factor_explain = "(最新价-开盘价)/(最高价-最低价),求均值/标准差" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "买单强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = ['T1mTickab']  # ["Next1mTickfulladdorder"]
    #
    # xdb_data = [
    #     {
    #    'name': 'xdb_trade', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
    #    'lag': 1 # 回看日期，N为往前回看1~N天
    # }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            tick_df = database['T1mTickab']
            #tick_df = generate_tick_trade_volume(tick_df)  # 公共函数
            tick_df = filter_930(tick_df)  # 公共函数
            database['T1mTickab'] = tick_df
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df = database['T1mTickab']  # .iloc[:120]
            #print(df.columns)
            if len(df) > 1:
                df['pct_chg'] = (df['LastPx'] - df['pre_close']) / (df['HighPx'] - df['LowPx'] + 1e-4)
                res3 =  df['pct_chg'].mean()/(1e-3+df['pct_chg'].std())#df['pct_chg'].median()
            else:
                res3 = 0

            factor_dict = {self.factor_name: res3}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
