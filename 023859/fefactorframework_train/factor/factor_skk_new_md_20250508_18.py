# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_skk_new_md_20250508_18(BaseFactor):
    strategy_name = "neptune"
    factor_name = "skk_new_md_20250508_18"
    fill_na_value = 0.007027
    need_pre_calculate_T_N = True
    owner = "skk"  # 开发人员姓名
    factor_explain = "涨跌幅的3日最大值" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['pct_chg', 'turn', 'open', 'close', 'pre_close', 'high', 'low', 'amt', 'vwap', 'adjfactor']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            # df_ori = df_ori[df_ori['amt'] > 0]
            ########################
            df_ori['open'] = df_ori['open'] * df_ori['adjfactor']
            df_ori['close'] = df_ori['close'] * df_ori['adjfactor']
            df_ori['high'] = df_ori['high'] * df_ori['adjfactor']
            df_ori['low'] = df_ori['low'] * df_ori['adjfactor']
            df_ori['vwap'] = df_ori['vwap'] * df_ori['adjfactor']
            df_ori['pre_close'] = df_ori['pre_close'] * df_ori['adjfactor']
            ########################
            # df_ori['pct_chg'] = df_ori['pct_chg'].unstack().fillna(method='ffill', limit=80).stack()
            df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (df_ori.reset_index()['dt'] >= '2020-08-24')) | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            df_ori.loc[df_ori['zcz'] == 1, 'pct_chg'] = df_ori.loc[df_ori['zcz'] == 1, 'pct_chg'] / 2
            #####################
            if self.zcz_adjusted == "是":
                df_ori['weight'] = 1
                condition = (((df_ori.reset_index()["Ticker"].apply(lambda x:x[0]=='3')) & (df_ori.reset_index()["dt"] >= '20200824')) | (df_ori.reset_index()["Ticker"].apply(lambda x:x[0:2]=='68'))).values
                df_ori['weight'].loc[condition] = 2
                def zhucezhi_help(md_data, column):
                    md_data[column] = ((md_data[column] / md_data['pre_close'] - 1) / md_data['weight'] + 1) * md_data['pre_close']
                zhucezhi_help(df_ori, 'high')
                zhucezhi_help(df_ori, 'low')
                zhucezhi_help(df_ori, 'open')
                zhucezhi_help(df_ori, 'close')
                zhucezhi_help(df_ori, 'vwap')
            #####################
            df_ori['aaa'] = (2 * df_ori['close'] - df_ori['high'] - df_ori['low']) / df_ori['open'] * 100
            df_ori[self.factor_name] = df_ori['aaa'].unstack().rolling(5, 1).mean().stack()
            # df_ori[self.factor_name] = df_ori['aaa']
            #####################
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
