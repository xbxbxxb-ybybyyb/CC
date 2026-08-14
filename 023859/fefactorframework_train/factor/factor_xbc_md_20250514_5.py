import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_md_20250514_5(BaseFactor):
    strategy_name = "neptune"
    factor_name = "xbc_md_20250514_5"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "xbc"  # 开发人员姓名
    factor_explain = "high close open low 的差的滚动平均" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, # 注意为正数
         'column': ['adjfactor','pct_chg','turn','high', 'low', 'open', 'vwap', 'close','pre_close', 'amt','volume']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                    df_ori.reset_index()['dt'] >= '2020-08-24'))
                             | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            df_ori['bj'] = (df_ori.reset_index()['Ticker'].apply(lambda x: x[-2:] == 'BJ')).values

            for col in ['high', 'low', 'open', 'vwap', 'close', 'pre_close']:
                df_ori[col] = (df_ori[col] * df_ori['adjfactor']).apply(lambda x: round_(x, 4))
            for col in ['volume']:
                df_ori[col] = (df_ori[col] / df_ori['adjfactor']).apply(lambda x: round_(x, 4))
            # -------------------------------------------------------------------------------------------------------------------
            def f_calc_avg(factor_series):
                return factor_series[~np.isnan(factor_series)].mean()
            def f_calc_std(factor_series):
                return factor_series[~np.isnan(factor_series)].std()
            df_ori['s1'] = ((df_ori['high'] + df_ori['close']) / df_ori['pre_close']/(0.1+df_ori['pct_chg']))**2
            df_ori['s2'] = ((df_ori['open'] + df_ori['low']) / df_ori['pre_close']/(0.1+df_ori['pct_chg']))**2
            df_ori['factor'] = df_ori['s1'] - df_ori['s2']
            df_ori[self.factor_name] = df_ori['factor'].unstack().rolling(4,1).apply(f_calc_std).stack() + \
                                       df_ori['factor'].unstack().rolling(18,1).apply(f_calc_std).stack().apply(lambda x : round_(x,5)).replace(0,np.nan)
            df_ori[self.factor_name] = df_ori[self.factor_name].apply(lambda x: round_(x, 4))
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
