import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 财务CS + MD
class factor_qyh_finance_new_test4(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_finance_new_test4"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时

    xdb_data = [{
        'name':'xdb_balancesheet_cs',
        'lag':4
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
            # finance
            df_balancesheet = database['xdb_balancesheet_cs']
            # df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT'].apply(int)
            #                                   >= df_balancesheet['S_INFO_LISTDATE'].apply(int)]
            res1 = (df_balancesheet['FIX_ASSETS'] + df_balancesheet['TOT_CUR_ASSETS']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(4).sum()).to_frame(name='res1')
            # MD
            md_data = database['MD_CHINA_STOCK_DAILY_WIND']
            res2 = md_data['amt'].unstack().rolling(5,1).max().iloc[[-1]]
            res2.index = [res1.index[0][0]] # 日期后移一天，便于对齐
            # 组合
            res1['res2'] = res2.stack()
            res1[self.factor_name] = res1['res1'] / res1['res2'].replace(0,np.nan)

            database['pre_T_N'] = res1[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res