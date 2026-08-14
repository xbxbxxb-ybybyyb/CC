# T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_tsq_neweuropa_20241226_1(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "jupiter/europa"
    factor_name = "tsq_neweuropa_20241226_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "tsq"  # 开发人员姓名
    factor_explain = "高价买卖单撤单数不平衡" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-订单结构" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = ['TCancelprice']
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
            data = database['TCancelprice']
            dt, ticker = data.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            pre_close = data['pre_close'].values[0]
            if zcz:
                data['OrderPrice'] = ((data['OrderPrice'] / pre_close - 1) / 2 + 1) * pre_close

            data = filter_930(data)
            cancel_buy_num = len(data[(data['OrderBSFlag'] == 1)&(data['OrderPrice']>=data['pre_close']*1.09)])
            cancel_sell_num = len(data[(data['OrderBSFlag'] == 2)&(data['OrderPrice']>=data['pre_close']*1.09)])

            res = (cancel_sell_num - cancel_buy_num)/(1e-6 + len(data))

            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
