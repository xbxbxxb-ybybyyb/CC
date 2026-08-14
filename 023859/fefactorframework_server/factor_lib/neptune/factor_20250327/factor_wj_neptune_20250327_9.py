import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_wj_neptune_20250327_9(BaseFactor):
    strategy_name = "neptune"
    factor_name = "wj_neptune_20250327_9"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "wj"  # 开发人员姓名
    factor_explain = "（委卖量-委卖量）/(委买价-委卖价)，求均值" # 因子逻辑解释
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
            if len(df) > 1:
                df['BidQty'] = df['TotalBidQty'] - df['TotalBidQty'].shift(1).fillna(0)
                df['OfferQty'] = df['TotalOfferQty'] - df['TotalOfferQty'].shift(1).fillna(0)

                res3 = ((df['BidQty'] - df['OfferQty'])/(df['WeightedAvgBidPx']-df['WeightedAvgOfferPx']+1e-3)).mean()
            else:
                res3 = 0

            factor_dict = {self.factor_name: res3}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
