import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_tsq_newneptune_20250403_35(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250403_35"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "日内价格偏度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 40,  # 注意为正数
         'column': ['close', 'pre_close']
         },
        {'name': 'minute5_close',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/minute5/close.h5',
         'lag': 40,  # 注意为正数
         'column': ['m930', 'm935', 'm940', 'm945', 'm950', 'm955', 'm1000','m1005', 'm1010', 'm1015', 'm1020', 'm1025', 'm1030', 'm1035', 'm1040','m1045', 'm1050', 'm1055', 'm1100', 'm1105', 'm1110', 'm1115', 'm1120',\
                    'm1125', 'm1300', 'm1305', 'm1310', 'm1315', 'm1320', 'm1325', 'm1330','m1335', 'm1340', 'm1345', 'm1350', 'm1355', 'm1400', 'm1405', 'm1410','m1415', 'm1420', 'm1425', 'm1430', 'm1435', 'm1440', 'm1445', 'm1450','m1455']
         }
    ]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD','minute5'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['minute5_close']
            df_ori['pre_close'] = database['MD_CHINA_STOCK_DAILY_WIND']['pre_close']
            df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (df_ori.reset_index()['dt'] >= '2020-08-24')) | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            df_ori['bj'] = (df_ori.reset_index()['Ticker'].apply(lambda x: x[-2:] == 'BJ')).values

            columns = ['m930', 'm935', 'm940', 'm945', 'm950', 'm955', 'm1000', 'm1005', 'm1010', 'm1015', 'm1020','m1025', 'm1030', 'm1035', 'm1040', 'm1045', 'm1050', 'm1055', 'm1100', 'm1105', 'm1110',\
                       'm1115', 'm1120', 'm1125', 'm1300', 'm1305', 'm1310', 'm1315', 'm1320', 'm1325', 'm1330', 'm1335', 'm1340','m1345', 'm1350', 'm1355', 'm1400', 'm1405', 'm1410', 'm1415', 'm1420', 'm1425',\
                       'm1430','m1435', 'm1440', 'm1445', 'm1450', 'm1455']
            for col in columns:
                df_ori.loc[df_ori['zcz'] == 1, col] = ((df_ori.loc[df_ori['zcz'] == 1, col] / df_ori.loc[df_ori['zcz'] == 1, 'pre_close'] - 1) / 2 + 1) * df_ori.loc[df_ori['zcz'] == 1, 'pre_close']
                df_ori.loc[df_ori['bj'] == 1, col] = ((df_ori.loc[df_ori['bj'] == 1, col] / df_ori.loc[df_ori['bj'] == 1, 'pre_close'] - 1) / 3 + 1) * df_ori.loc[df_ori['bj'] == 1, 'pre_close']
            # -------------------------------------------------------------------------------------------------------------------
            df_ori['factor'] = df_ori.skew(axis=1)
            df_ori['factor'] = df_ori['factor'].unstack().rolling(20,1).std().stack()
            df_ori[self.factor_name] = df_ori['factor'].apply(lambda x : round_(x,5))
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
