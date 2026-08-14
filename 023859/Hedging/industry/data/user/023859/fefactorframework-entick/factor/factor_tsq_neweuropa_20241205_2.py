# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_neweuropa_20241205_2(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "jupiter/europa"
    factor_name = "tsq_neweuropa_20241205_2"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "新增流动性与消失流动性之差" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "放量角度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = ['TTransaction','TOrder','TCancelprice']
    xdb_data = []
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
            data_trans = database['TTransaction']
            data_order = database['TOrder']
            data_cancel = database['TCancelprice']
            data_trans_new = data_trans[data_trans['TradePrice'] > 0]
            data_order_new = data_order[~data_order['OrderIndex'].isin(data_cancel['OrderIndex'])]
            cancel_buy_amt = (data_cancel[data_cancel['OrderBSFlag'] == 1]['OrderQty']*data_cancel[data_cancel['OrderBSFlag'] == 1]['OrderPrice']).sum()
            cancel_sell_amt = (data_cancel[data_cancel['OrderBSFlag'] == 2]['OrderQty']*data_cancel[data_cancel['OrderBSFlag'] == 2]['OrderPrice']).sum()

            buy_new_liquity = (data_order_new[data_order_new['OrderBSFlag'] == 1]['OrderQty']*data_order_new[data_order_new['OrderBSFlag'] == 1]['OrderPrice']).sum()
            sell_new_liquity = (data_order_new[data_order_new['OrderBSFlag'] == 2]['OrderQty']*data_order_new[data_order_new['OrderBSFlag'] == 2]['OrderPrice']).sum()

            buy_new_net_liquity = buy_new_liquity - (data_trans_new[data_trans_new['TradeBSFlag'] == 1]['TradeMoney'].sum() + cancel_buy_amt)
            sell_new_net_liquity = sell_new_liquity - (data_trans_new[data_trans_new['TradeBSFlag'] == 2]['TradeMoney'].sum() + cancel_sell_amt)
            res = buy_new_net_liquity - sell_new_net_liquity
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
