import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *


class factor_tsq_newneptune_20250508_3(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250508_3"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "买卖下单vwap之差"  # 因子逻辑解释
    zcz_adjusted = "是"  # 是否针对注册制调整：是/否
    logic_type = ""  # 逻辑类别
    low_cost = "是"  # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
            'name': 'xdb_order1m',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 3  # 回看日期，N为往前回看1~N天
        }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_order1m']
        dt, ticker = data.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        pre_close = data['pre_close'].values[0]
        if zcz:
            data['OrderPrice_buy_mean'] = ((data['OrderPrice_buy_mean'] / pre_close - 1) / 2 + 1) * pre_close
            data['OrderPrice_sell_mean'] = ((data['OrderPrice_sell_mean'] / pre_close - 1) / 2 + 1) * pre_close
        data = filter_930(data)
        buy_vwap = (data['OrderPrice_buy_mean']*data['OrderQty_buy']).sum() / data['OrderQty_buy'].sum()
        sell_vwap = (data['OrderPrice_sell_mean']*data['OrderQty_sell']).sum() / data['OrderQty_sell'].sum()
        res = (buy_vwap - sell_vwap) / pre_close
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
