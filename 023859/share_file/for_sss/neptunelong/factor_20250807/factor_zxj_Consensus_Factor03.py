import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor03(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Consensus_Factor03"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "分析师对EPS和PE一致预期变化幅度的等权和" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'DWD_EXP_FORECASTSECUDERIVED', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/DWD_EXP_FORECASTSECUDERIVED/DWD_EXP_FORECASTSECUDERIVED.h5', #DWD_EXP_FORECASTSECUDERIVED
         'lag': 100,
         'column':['FORECASTPE','FORECASTEPS']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['SUNTIME'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_exp_secu_derived = database['DWD_EXP_FORECASTSECUDERIVED'] # 和上面t-1_factor_data的name一致
            
            pe_63d_ago = df_exp_secu_derived.groupby('Ticker')['FORECASTPE'].shift(63)
            pe_change = (df_exp_secu_derived['FORECASTPE'] - pe_63d_ago) / abs(pe_63d_ago)
            factor_df_pe = pd.DataFrame(pe_change)
            factor_df_pe.rename(columns={'FORECASTPE': 'pe_change'}, inplace=True)
            factor_df_pe.replace([np.inf, -np.inf], np.nan, inplace=True)

            eps_63d_ago = df_exp_secu_derived.groupby('Ticker')['FORECASTEPS'].shift(63)
            eps_change = (df_exp_secu_derived['FORECASTEPS'] - eps_63d_ago) / abs(eps_63d_ago)
            factor_df_eps = pd.DataFrame(eps_change)
            factor_df_eps.rename(columns={'FORECASTEPS': 'eps_change'}, inplace=True)
            factor_df_eps.replace([np.inf, -np.inf], np.nan, inplace=True)

            pe_eps_change_df = factor_df_eps.join(factor_df_pe, how='inner')
            pe_eps_change_df['rank_eps_change'] = pe_eps_change_df.groupby(level='dt')['eps_change'].rank(pct=True)
            pe_eps_change_df['rank_pe_change'] = pe_eps_change_df.groupby(level='dt')['pe_change'].rank(pct=True)
            pe_eps_change_df[self.factor_name] = pe_eps_change_df['rank_eps_change'] - pe_eps_change_df['rank_pe_change']
            
            database['pre_T_N'] = pe_eps_change_df[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
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
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res