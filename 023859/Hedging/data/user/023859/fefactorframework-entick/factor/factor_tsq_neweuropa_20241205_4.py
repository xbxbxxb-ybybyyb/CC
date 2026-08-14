# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_neweuropa_20241205_4(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "jupiter/europa"
    factor_name = "tsq_neweuropa_20241205_4"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "订单薄不平衡" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "筹码分布" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = ['TTick1s']
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
            data = database['TTick1s']
            data = filter_930(data)
            data = fun_zcz_tick(data)
            omega = [1 - (i) / 10 for i in range(10)]
            data['WeightedAvgBidVlm'] = np.sum([omega[i] * data[f'Buy{i + 1}OrderQty'] for i in range(10)]) / np.sum(omega)
            data['WeightedAvgOfferVlm'] = np.sum([omega[i] * data[f'Sell{i + 1}OrderQty'] for i in range(10)]) / np.sum(omega)
            data['DeltaVlmBid'] = 0
            data.loc[data['Buy1Price'].diff() == 0, 'DeltaVlmBid'] = data['WeightedAvgBidVlm'].diff()[data['Buy1Price'].diff() == 0]
            data.loc[data['Buy1Price'].diff() > 0, 'DeltaVlmBid'] = data['WeightedAvgBidVlm'][data['Buy1Price'].diff() > 0]
            data['DeltaVlmAsk'] = 0
            data.loc[data['Sell1Price'].diff() == 0, 'DeltaVlmAsk'] = data['WeightedAvgOfferVlm'].diff()[data['Sell1Price'].diff() == 0]
            data.loc[data['Sell1Price'].diff() < 0, 'DeltaVlmAsk'] = data['WeightedAvgOfferVlm'][data['Sell1Price'].diff() < 0]
            res = np.mean((data['DeltaVlmBid'] - data['DeltaVlmAsk']) / (data['DeltaVlmBid'] + data['DeltaVlmAsk']))
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
