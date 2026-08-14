import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *


class factor_tsq_newneptune_20250508_16(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250508_16"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "聪明钱vwap占比"  # 因子逻辑解释
    zcz_adjusted = "是"  # 是否针对注册制调整：是/否
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
        data = fun_zcz_tick(data)
        data = filter_930(data)
        data['vol'] = data['TotalVolumeTrade'] - data['TotalVolumeTrade'].shift(1).fillna(0)
        data['LastPx'] = data['LastPx'].replace(0, np.nan)
        data['LastPx'] = data['LastPx'].ffill()
        data['ret'] = data['LastPx'].pct_change()
        data = data.sort_values(by='ret')
        data['cumvol'] = data['vol'].cumsum()
        data_smart = data[data['cumvol'] >= 0.2 * data['vol'].sum()]
        smart_vwap = np.sum(data_smart['vol'] * data_smart['LastPx']) / np.sum(data_smart['vol'])
        all_vwap = np.sum(data['vol'] * data['LastPx']) / np.sum(data['vol'])
        res = smart_vwap / all_vwap

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
