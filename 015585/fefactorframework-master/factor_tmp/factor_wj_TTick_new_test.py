# h5 + xdb + T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_wj_TTick_new_test(BaseFactor):
    strategy_name = "saturn"
    factor_name = "wj_TTick_new_test"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wj"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格形态" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_tickex', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        df = database['xdb_tickex']
        df = df[df['LastPx'] > 0]
        df = df[df['MDTime'] >= 93500000]  # 选择连续竞价阶段的tick数据
        df = df[df['MDTime'] <= 100000000]

        df['VolumeTrade'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(1).fillna(0)
        df['ret'] = (df['Buy1OrderQty'] - df['Sell1OrderQty']) / (1e-3 + df['VolumeTrade'])
        res = df['ret'].std()
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)