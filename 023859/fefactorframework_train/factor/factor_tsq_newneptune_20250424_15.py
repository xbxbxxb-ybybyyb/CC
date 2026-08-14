import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *


class factor_tsq_newneptune_20250424_15(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250424_15"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "放量时刻成交量与过去五分钟最大成交量的相关系数"  # 因子逻辑解释
    zcz_adjusted = "否"  # 是否针对注册制调整：是/否
    logic_type = ""  # 逻辑类别
    low_cost = "是"  # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
            'name': 'xdb_tick1m',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 3  # 回看日期，N为往前回看1~N天
        }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m']
        data = filter_930(data)
        data_all = []
        for date in data.index.get_level_values(0).unique():
            data_ = data.loc[date]
            data_['vol'] = data_['TotalVolumeTrade'] - data_['TotalVolumeTrade'].shift(1).fillna(0)
            data_['vol_max'] = data_['vol'].shift(-5).rolling(5).max()
            data_smart = data_[data_['vol'] >= data_['vol'].quantile(0.8)]
            data_all.append(data_smart)
        data_all = pd.concat(data_all)
        res = data_all['vol'].corr(data_all['vol_max'], method='spearman')

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
