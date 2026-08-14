# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_newsaturn_20250320_6(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "saturn"
    factor_name = "tsq_newsaturn_20250320_6"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "卖单消失流动性" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "放量角度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = []
    xdb_data = [
        {
            'name': 'xdb_trade',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 3  # 回看日期，N为往前回看1~N天
        },
        {
            'name': 'xdb_cancel',  # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
            'lag': 3  # 回看日期，N为往前回看1~N天
        }
    ]
    t_1_factor_data = []
    #     {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
    #      'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
    #      'lag': 20, #注意为正数
    #      'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap']
    # }]
    t_1_factor_data_types = []#['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data_trans = database['xdb_trade']
        data_trans = filter_930(data_trans)
        data_trans = filter_transaction(data_trans)
        data_cancel = database['xdb_cancel']
        data_cancel = filter_930(data_cancel)
        res = 0
        for date in data_trans.index.get_level_values(0).unique():
            data_trans_date = data_trans.loc[date]
            data_cancel_date = data_cancel.loc[date]
            data_trans_new = data_trans_date[data_trans_date['TradePrice'] > 0]
            cancel_buy_amt = (data_cancel_date[data_cancel_date['OrderBSFlag'] == 1]['OrderQty'] *data_cancel_date[data_cancel_date['OrderBSFlag'] == 1]['OrderPrice']).sum()
            sell_new_net_liquity = data_trans_new[data_trans_new['TradeBSFlag'] == 2]['TradeMoney'].sum() + cancel_buy_amt
            res += sell_new_net_liquity
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res / 2]})
        return database

    def prepare_T_data(self, database):
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
