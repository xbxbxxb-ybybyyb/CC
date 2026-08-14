import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_tsq_newneptune_20250417_19(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250417_19"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "买卖不平衡变种" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m']
        data = fun_zcz_tick(data)
        data_all = []
        for date in data.index.get_level_values(0).unique():
            data_ = data.loc[date]
            data_ = filter_930(data_)

            data_['DeltaBid1Price'] = data_['Buy1Price'].diff()
            data_['DeltaAsk1Price'] = data_['Sell1Price'].diff()
            data_['DeltaBid1Qty'] = data_['Buy1OrderQty'].diff()
            data_['DeltaAsk1Qty'] = data_['Sell1OrderQty'].diff()

            data_.loc[(data_['DeltaBid1Price'] > 0), 'OF1Bid'] = data_.loc[(data_['DeltaBid1Price'] > 0), 'Buy1OrderQty']
            data_.loc[(data_['DeltaBid1Price'] < 0), 'OF1Bid'] = -data_.loc[(data_['DeltaBid1Price'] < 0), 'Buy1OrderQty']
            data_.loc[(data_['DeltaBid1Price'] == 0), 'OF1Bid'] = data_.loc[(data_['DeltaBid1Price'] == 0), 'DeltaBid1Qty']

            data_.loc[(data_['DeltaAsk1Price'] > 0), 'OF1Ask'] = -data_.loc[(data_['DeltaAsk1Price'] > 0), 'Sell1OrderQty']
            data_.loc[(data_['DeltaAsk1Price'] < 0), 'OF1Ask'] = data_.loc[(data_['DeltaAsk1Price'] < 0), 'Sell1OrderQty']
            data_.loc[(data_['DeltaAsk1Price'] == 0), 'OF1Ask'] = data_.loc[(data_['DeltaAsk1Price'] == 0), 'DeltaAsk1Qty']
            data_all.append(data_)

        data_all = pd.concat(data_all)
        res = (1e4 * (data_all['OF1Bid'] - data_all['OF1Ask']) / (data_all['Sell1OrderQty'] + data_all['Buy1OrderQty'])).autocorr()

        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
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
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
