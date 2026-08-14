import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xly_neptune_t_1_a40(BaseFactor):
    strategy_name = "neptune"
    factor_name = "xly_neptune_t_1_a40"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xly"  # 开发人员姓名
    factor_explain = "行业内均值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30,
         'column': ['high','close','amt','vwap','low','open','volume','turn']},
        {'name': 'RISK_CHINA_STOCK_DAILY_STYLEFACTOR',
         'path': '/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',
         'lag': 30,
         'column': ['Industry']}
    ]
    t_1_factor_data_types = ['MD','RISK']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND']  # 和上面t-1_factor_data的name一致
            df_ori['factor'] = (df_ori['high'] - df_ori['vwap'])/(df_ori['high']-df_ori['low']+1)
            df_ori['Ind'] = database['RISK_CHINA_STOCK_DAILY_STYLEFACTOR']['Industry']
            df_ori['date'] = df_ori.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
            ind_df = df_ori.groupby(['date', 'Ind'])[['factor']].mean()
            ind_df.columns = ['factor_ind']
            df_ori2 = pd.merge(df_ori[['date', 'Ind', 'factor']], ind_df, left_on=['date', 'Ind'], right_index=True, how='left')
            df_ori2[self.factor_name] = df_ori2['factor_ind'].unstack().rolling(20, min_periods=1).mean().stack()
            df_ori2[self.factor_name] = df_ori2[self.factor_name].apply(lambda x: round_(x, 5))
            database['pre_T_N'] = df_ori2[[self.factor_name]]
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
            res = database['pre_T_N']
            return res
