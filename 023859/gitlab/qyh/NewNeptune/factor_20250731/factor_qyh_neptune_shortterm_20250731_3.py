import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptune_shortterm_20250731_3(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_shortterm_20250731_3"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "买卖挂量 统计量" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "短周期-总量强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            tick_df = database['xdb_tick1m']
            pre_close = tick_df['pre_close'].max()
            ff_shares = tick_df['ff_shares'].max()
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            tick_df['MDTime_delta'] = tick_df['MDTime'].apply(
                    lambda x: get_time_delta(x) - 1800000) # 距离930毫秒数
            tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
            tick_df = filter_930(tick_df)
            #
            tick_df['factor'] = (tick_df['Buy1OrderQty'] - tick_df['Buy1OrderQty'].shift(1)) / (tick_df['VolumeTrade']+1)
            res = tick_df['factor'].max()
            # if zcz:
            #     res = res/2
            #
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
