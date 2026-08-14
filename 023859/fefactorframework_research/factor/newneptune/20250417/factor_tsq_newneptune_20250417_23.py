import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *


class factor_tsq_newneptune_20250417_23(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250417_23"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "买卖挂单额变化不平衡"  # 因子逻辑解释
    zcz_adjusted = "否"  # 是否针对注册制调整：是/否
    logic_type = ""  # 逻辑类别
    low_cost = "是"  # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
            'name': 'xdb_tick1m',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 1  # 回看日期，N为往前回看1~N天
        }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m']
        data['BidAdd'] = data['TotalBidQty'] - data['TotalBidQty'].shift(1).fillna(0)
        data['AskAdd'] = data['TotalOfferQty'] - data['TotalOfferQty'].shift(1).fillna(0)
        if len(data['TotalValueTrade']):
            res = 1e4 * (data['BidAdd'] - data['AskAdd']).mean() / (1e-8 + data['TotalValueTrade'].iloc[-1] - data['TotalValueTrade'].iloc[0])
        else:
            res = np.nan

        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
