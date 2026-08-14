# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *


class factor_ssr_net_s_s4_120(BaseFactor):
    strategy_name = "neptune"
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    factor_period = int(factor_name.split('_')[-1])
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "sss"  # 开发人员姓名
    factor_explain = "资金流入比例因子" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    t_1_factor_data = [{'name': 'MD',
                        'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                        'lag': factor_period+5,
                        'column': ['amt','pct_chg']},
                       {'name': 'AShareMoneyFlow',
                        'path': '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5',
                        'lag': factor_period + 5,
                        'column': ['BUY_VALUE_SMALL_ORDER', 'SELL_VALUE_SMALL_ORDER']},
                       ]
    t_1_factor_data_types = ['MD','AShareMoneyFlow'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        factor_name=self.factor_name
        factor_period = self.factor_period
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['MD']

            mf = database['AShareMoneyFlow']
            mf['net']=mf['BUY_VALUE_SMALL_ORDER']-mf['SELL_VALUE_SMALL_ORDER']
            mf['amt']=md['amt']/10
            fenzi = mf['net'].unstack().rolling(factor_period, min_periods=1).sum()
            fenmu = mf['amt'].unstack().rolling(factor_period, min_periods=1).sum()
            fenzi[fenzi.abs() < 1] = 0
            fenmu[fenmu.abs() < 1] = 0
            flow = fenzi / fenmu.replace(0,np.nan)
            flow[flow > 1] = 1
            flow[flow < -1] = -1
            ratio = flow.copy()

            df = pd.DataFrame(ratio.round(4).rank(axis=1, pct=True).round(4).stack())-0.5
            df.columns = [factor_name]
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
