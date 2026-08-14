import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *


class factor_tsq_newneptune_20250417_25(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250417_25"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "平均收益率变化指标"  # 因子逻辑解释
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
        data_all = []
        for date in data.index.get_level_values(0).unique():
            data_ = data.loc[date]
            data_ = generate_tick_trade_value(data_)
            data_ = generate_tick_trade_volume(data_)
            data_['AvgPx'] = data_['ValueTrade'] / data_['VolumeTrade'].replace(0,np.nan)
            data_['AvgPx'] = data_['AvgPx'].replace(0, np.nan)
            data_['AvgPx'] = data_['AvgPx'].ffill()
            data_['d_ret'] = np.log(1 + data_['AvgPx'] - data_['AvgPx'].shift(1))
            data_['s_ret'] = data_['AvgPx'].pct_change()
            data_['d_ret'] = data_['d_ret'].replace([-np.inf,np.inf],np.nan)
            data_['s_ret'] = data_['s_ret'].replace([-np.inf,np.inf],np.nan)
            data_ = filter_930(data_)
            data_all.append(data_)
        data_all = pd.concat(data_all)
        res = 1e2 * ((data_all['s_ret'] - data_all['d_ret']) * 2 - data_all['s_ret'] ** 2).mean()

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
