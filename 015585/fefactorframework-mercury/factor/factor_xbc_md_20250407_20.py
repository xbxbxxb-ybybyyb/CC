# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_md_20250407_20(BaseFactor):
    strategy_name = "europa"
    factor_name = "xbc_md_20250407_20"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xbc"  # 开发人员姓名
    factor_explain = "kdj" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 300, #注意为正数
         'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap', 'open', 'low', 'high', 'close', 'adjfactor']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                    md.reset_index()['dt'] >= '2020-08-24'))
                         | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            factor_name = self.factor_name
            md_data = md

            def cal_kdj(df, period, col,para):
                df['low1'] = df['low'].unstack().rolling(period, min_periods=2).min().stack()
                df['high1'] = df['high'].unstack().rolling(period, min_periods=2).max().stack()
                rsv = (df['close'] - df['low1']) / (df['high1'] - df['low1'])
                df['rsv'] = rsv
                df['k'] = pd.DataFrame(rsv).ewm(com=para).mean()
                df['d'] = df['k'].ewm(com=para).mean()
                df['j'] = 3 * df['k'] - 2 * df['d']
                return df[col]

            md_data['close'] = md_data['close'] * md_data['adjfactor']
            md_data['high'] = md_data['high'] * md_data['adjfactor']
            md_data['low'] = md_data['low'] * md_data['adjfactor']
            ########################
            factor_df = pd.DataFrame()
            col = 'k'
            para = 0.5
            md_data['stat2'] = cal_kdj(md_data, 5,col,para)
            md_data['stat3'] = cal_kdj(md_data, 7,col,para)
            md_data['stat4'] = cal_kdj(md_data, 9,col,para)
            md_data['stat5'] = cal_kdj(md_data, 11,col,para)
            factor_df[factor_name] = 2*md_data[['stat2','stat3','stat4','stat5']].min(axis=1)
            col = 'd'
            md_data['stat2'] = cal_kdj(md_data, 5, col, para)
            md_data['stat3'] = cal_kdj(md_data, 7, col, para)
            md_data['stat4'] = cal_kdj(md_data, 9, col, para)
            md_data['stat5'] = cal_kdj(md_data, 11, col, para)
            factor_df[factor_name] -= md_data[[ 'stat2', 'stat3', 'stat4', 'stat5']].min(axis=1)
            col = 'j'
            md_data['stat2'] = cal_kdj(md_data, 5, col, para)
            md_data['stat3'] = cal_kdj(md_data, 7, col, para)
            md_data['stat4'] = cal_kdj(md_data, 9, col, para)
            md_data['stat5'] = cal_kdj(md_data, 11, col, para)
            factor_df[factor_name] -= md_data[[ 'stat2', 'stat3', 'stat4', 'stat5']].min(axis=1)
            # -------------------------------------------------------------------------------------------------------------------
            md_data[factor_name] = factor_df[factor_name].apply(lambda x: round_(x, 4))
            database['pre_T_N'] = md_data[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
