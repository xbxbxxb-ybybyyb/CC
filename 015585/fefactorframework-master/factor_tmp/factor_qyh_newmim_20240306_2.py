# h5
# 验证新sft的准确性
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newmim_20240306_2(BaseFactor):
    owner = 'qyh'
    strategy_name = "mimas"
    factor_name = "qyh_newmim_20240306_2"
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    fill_na_value = 0
    need_pre_calculate_T_N = True # 纯T日数据不需要pre_T_N
    #
    xdb_data = [{
       'name': 'xdb_tickex', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]
    t_day_data = []
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        else:
            tick_df = database['xdb_tickex']
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
            tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
            tick_df = tick_df[tick_df['MDTime'] >= 93000000]
            tick_df = tick_df[tick_df['MDTime'] < 145700000]
            tick_df['factor'] = tick_df['WeightedAvgOfferPx'] / (tick_df['pre_close'])
            if zcz:
                tick_df['factor'] = (tick_df['factor'] - 1) / 2 + 1
            res = tick_df['factor'].head(1).mean() - tick_df['factor'].tail(1).mean()
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
            return database
    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
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
