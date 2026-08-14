import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_md_corr_demo(BaseFactor):
    strategy_name = "neptune"
    factor_name = "md_corr_demo"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['adjfactor', 'vwap', 'close','pre_close', 'amt']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    '''
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    '''
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            for col in ['vwap', 'close']:
                df_ori[col] = df_ori[col] * df_ori['adjfactor']
            for col in ['amt','pre_close']:
                df_ori = df_ori[df_ori[col] > 0]
            # -------------------------------------------------------------------------------------------------------------------
            x = 'close'
            y = 'vwap'
            df_ori['xy'] = df_ori[x] * df_ori[y]
            df_ori['exy'] = df_ori['xy'].unstack().rolling(20, 5).mean().stack().apply(lambda x : round_(x,5))
            df_ori['ex'] = df_ori[x].unstack().rolling(20, 5).mean().stack().apply(lambda x : round_(x,5))
            df_ori['ey'] = df_ori[y].unstack().rolling(20, 5).mean().stack().apply(lambda x : round_(x,5))
            df_ori['stdx'] = df_ori[x].unstack().rolling(20, 5).std().stack().apply(lambda x : round_(x,5))
            df_ori['stdy'] = df_ori[y].unstack().rolling(20, 5).std().stack().apply(lambda x : round_(x,5))
            df_ori['factor'] = (df_ori['exy'] - df_ori['ex'] * df_ori['ey']) \
                               / (df_ori['stdx'] * df_ori['stdy']).apply(lambda x : round_(x,5)).replace(0,np.nan)
            df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
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
