import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# T日CS + xdb_cs + MD
class factor_qyh_finance_new_test5(BaseFactor):
    strategy_name = "saturn"
    factor_name = "qyh_finance_new_test5"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_day_data = ['T1mTickab_cs']
    xdb_data = [
        {'name':'xdb_tickex_cs',
         'lag':2
         }]
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 20,
         'column': ['amt']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            # xdb
            xdb_tickex_cs = database['xdb_tickex_cs']
            res1 = xdb_tickex_cs.groupby(['dt','Ticker']).apply(lambda x : x['LastPx'].mean()).to_frame(name='res1')
            # MD
            md_data = database['MD_CHINA_STOCK_DAILY_WIND']
            res2 = md_data['amt'].unstack().rolling(5,1).max().iloc[[-1]]
            res2.index = [res1.index[0][0]] # 日期后移一天，便于对齐
            # 组合
            res1['res2'] = res2.stack()
            res1[self.factor_name] = res1['res1'] + res1['res2']

            database['pre_T_N'] = res1[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_T1mTickab_cs = filter_930(database['T1mTickab_cs'])
            database['T1mTickab_cs'] = df_T1mTickab_cs
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res1 = database['pre_T_N']
            tick_df = database['T1mTickab_cs']
            if tick_df.empty:
                res2 = pd.DataFrame(columns = ['t_result'])
            else:
                res2 = tick_df.groupby(['dt','Ticker']).apply(lambda x : x['LastPx'].mean()).to_frame(name='t_result')
            res2['t_n_result'] = res1[self.factor_name]
            res2[self.factor_name] = res2['t_n_result'] + res2['t_result']

            # ---------------------------------------------------------------------------------------------------------------
            return res2[[self.factor_name]]