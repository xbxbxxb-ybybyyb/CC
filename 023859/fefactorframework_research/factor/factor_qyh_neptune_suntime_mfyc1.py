import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 卖方预测 cs
class factor_qyh_neptune_suntime_mfyc1(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_neptune_suntime_mfyc1"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
        'name':'xdb_researchreport_cs',
        'lag':250
        }
    ]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_mfyc = database['xdb_researchreport_cs']
            df_mfyc = df_mfyc[(df_mfyc['FORECASTQUARTER'] == 4) & (1-df_mfyc['FORECASTOR'].isna())] # 只取年报预测，且营收预测非空
            df_mfyc['year'] = df_mfyc.index[0][0].year
            df_mfyc = df_mfyc[df_mfyc['FORECASTYEAR'] == df_mfyc['year']] # 预测年份为计算日期对应的年份
            # -------------------------------------------------------------------------------------------------------------------
            res = df_mfyc.groupby(['dt', 'Ticker']).apply(lambda x : x.tail(5)['FORECASTOR'].mean() / x['FORECASTOR'].mean()).to_frame(name=self.factor_name) #
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
